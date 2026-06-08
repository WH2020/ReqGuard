#!/usr/bin/env python3
"""Validate ReqGuard workflow documents.

Supports both docs/reqguard and docs/ai-workflow.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


VALID_PROFILES = {"software-app", "embedded-firmware", "algorithm-model", "multi-domain"}
VALID_PHASES = {
    "intake",
    "requirements_draft",
    "requirements_review",
    "requirements_confirmed",
    "module_design",
    "implementation_ready",
    "task_alignment",
    "implementing",
    "verifying",
    "done",
    "change_proposal",
    "impact_analysis",
    "blocked",
}
REQ_RE = re.compile(r"\bREQ-\d{3,}\b")
MOD_RE = re.compile(r"\bMOD-\d{3,}\b")
EXP_RE = re.compile(r"\bEXP-[A-Z0-9-]+\b")
SECTION_RE = re.compile(r"^##\s+((?:REQ-\d{3,})|(?:MOD-\d{3,})|(?:EXP-[A-Z0-9-]+))\b(.*)$", re.MULTILINE)


def find_docs_dir(root: Path) -> Path | None:
    for rel in ("docs/reqguard", "docs/ai-workflow"):
        candidate = root / rel
        if candidate.exists():
            return candidate
    return None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json(path: Path) -> tuple[dict | None, str | None]:
    if not path.exists():
        return None, f"missing {path}"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as exc:
        return None, f"{path}: invalid JSON: {exc}"


def section_blocks(text: str, prefix: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(text))
    blocks: dict[str, str] = {}
    for idx, match in enumerate(matches):
        item_id = match.group(1)
        if not item_id.startswith(prefix):
            continue
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        blocks[item_id] = text[start:end]
    return blocks


def field_value(block: str, field: str) -> str | None:
    pattern = re.compile(rf"^\s*-\s*{re.escape(field)}:\s*(.*)$", re.MULTILINE | re.IGNORECASE)
    match = pattern.search(block)
    if not match:
        return None
    return match.group(1).strip()


def has_acceptance(block: str) -> bool:
    value = field_value(block, "Acceptance")
    if value:
        return True
    return bool(re.search(r"^\s*-\s*Acceptance:\s*$[\s\S]*?^\s*-\s+\S", block, re.MULTILINE))


def validate(root: Path) -> tuple[list[str], list[str], Path | None]:
    errors: list[str] = []
    warnings: list[str] = []
    docs = find_docs_dir(root)
    if not docs:
        return ["missing docs/reqguard or docs/ai-workflow"], warnings, None

    state, state_error = read_json(docs / "state.json")
    if state_error:
        errors.append(state_error)
        state = {}

    active_profiles: set[str] = set()
    if state:
        project_profile = state.get("project_profile")
        active = state.get("active_profiles")
        if not project_profile:
            errors.append("state.json missing project_profile")
        elif project_profile not in VALID_PROFILES:
            errors.append(f"state.json project_profile is invalid: {project_profile}")
        if not isinstance(active, list) or not active:
            errors.append("state.json active_profiles must be a non-empty list")
        else:
            active_profiles = set(str(item) for item in active)
            invalid = sorted(active_profiles - VALID_PROFILES)
            if invalid:
                errors.append(f"state.json active_profiles contains invalid profiles: {', '.join(invalid)}")
        phase = state.get("phase")
        if phase and phase not in VALID_PHASES:
            errors.append(f"state.json phase is invalid: {phase}")
        managed = state.get("managed_fields", {})
        if not managed.get("hook_owned") or not managed.get("agent_suggested"):
            warnings.append("state.json managed_fields should declare hook_owned and agent_suggested")

    req_text = read_text(docs / "requirements.md")
    mod_text = read_text(docs / "modules.md")
    trace_text = read_text(docs / "traceability.md")
    expert_text = read_text(docs / "expert_regions.md")

    if not req_text:
        errors.append("missing requirements.md")
    if not mod_text:
        errors.append("missing modules.md")
    if not trace_text:
        warnings.append("missing traceability.md")

    req_ids = REQ_RE.findall(req_text)
    mod_ids = MOD_RE.findall(mod_text)
    for item_type, ids in (("requirement", req_ids), ("module", mod_ids)):
        duplicates = sorted({item for item in ids if ids.count(item) > 1})
        if duplicates:
            warnings.append(f"duplicate {item_type} references found: {', '.join(duplicates)}")

    req_blocks = section_blocks(req_text, "REQ")
    mod_blocks = section_blocks(mod_text, "MOD")
    expert_blocks = section_blocks(expert_text, "EXP")

    for req_id, block in req_blocks.items():
        status = (field_value(block, "Status") or "").lower()
        profile = field_value(block, "Profile")
        if not profile:
            errors.append(f"{req_id} missing Profile")
        elif active_profiles and profile not in active_profiles:
            warnings.append(f"{req_id} profile {profile} is not in active_profiles")
        if status == "confirmed" and not has_acceptance(block):
            errors.append(f"{req_id} is confirmed but has no Acceptance")
        if status == "confirmed" and trace_text and req_id not in trace_text:
            warnings.append(f"{req_id} is confirmed but not present in traceability.md")

    for mod_id, block in mod_blocks.items():
        profile = field_value(block, "Profile")
        if not profile:
            errors.append(f"{mod_id} missing Profile")
        elif active_profiles and profile not in active_profiles:
            warnings.append(f"{mod_id} profile {profile} is not in active_profiles")
        if not re.search(r"Responsibilities:\s*(?:\n\s*-|\S)", block):
            warnings.append(f"{mod_id} should document Responsibilities")
        if not re.search(r"Non-responsibilities:\s*(?:\n\s*-|\S)", block):
            warnings.append(f"{mod_id} should document Non-responsibilities")

    active_expert_regions = set(state.get("active_expert_regions", [])) if state else set()
    if active_expert_regions and not expert_blocks:
        errors.append("state.json active_expert_regions is set but expert_regions.md is missing or empty")
    missing_active_regions = sorted(active_expert_regions - set(expert_blocks))
    if missing_active_regions:
        errors.append(f"state.json active_expert_regions references undefined regions: {', '.join(missing_active_regions)}")

    for region_id, block in expert_blocks.items():
        profile = field_value(block, "Profile")
        if not profile:
            errors.append(f"{region_id} missing Profile")
        elif active_profiles and profile not in active_profiles:
            warnings.append(f"{region_id} profile {profile} is not in active_profiles")
        if active_expert_regions and region_id not in active_expert_regions:
            warnings.append(f"{region_id} is defined but not listed in active_expert_regions")
        owned_reqs = set(REQ_RE.findall(block))
        owned_mods = set(MOD_RE.findall(block))
        for req_id in sorted(owned_reqs):
            if req_id not in req_blocks:
                errors.append(f"{region_id} references unknown requirement {req_id}")
        for mod_id in sorted(owned_mods):
            if mod_id not in mod_blocks:
                errors.append(f"{region_id} references unknown module {mod_id}")

    if trace_text:
        for req_id in sorted(set(REQ_RE.findall(trace_text))):
            if req_id not in req_blocks:
                errors.append(f"traceability.md references unknown requirement {req_id}")
        for mod_id in sorted(set(MOD_RE.findall(trace_text))):
            if mod_id not in mod_blocks:
                errors.append(f"traceability.md references unknown module {mod_id}")

    task_context_path = docs / "task_context.json"
    if task_context_path.exists():
        task_context, task_error = read_json(task_context_path)
        if task_error:
            errors.append(task_error)
        elif task_context:
            if task_context.get("generated_by") != "match_task_context.py":
                warnings.append("task_context.json generated_by should be match_task_context.py")
            if "profile_matches" not in task_context:
                errors.append("task_context.json missing profile_matches")
            if expert_blocks and "expert_region_matches" not in task_context:
                errors.append("task_context.json missing expert_region_matches")
            if "confidence" not in task_context:
                warnings.append("task_context.json should include confidence")
            if task_context.get("blocking") is True:
                warnings.append("task_context.json blocking=true; implementation should be blocked")

    return errors, warnings, docs


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ReqGuard workflow documents.")
    parser.add_argument("--root", default=".", help="Project root. Defaults to current directory.")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors, warnings, docs = validate(root)
    result = {
        "root": str(root),
        "docs_dir": str(docs) if docs else None,
        "errors": errors,
        "warnings": warnings,
        "ok": not errors,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("ReqGuard validation")
        print(f"Root: {root}")
        print(f"Docs: {docs if docs else 'not found'}")
        for error in errors:
            print(f"[ERROR] {error}")
        for warning in warnings:
            print(f"[WARN] {warning}")
        print("[OK] validation passed" if not errors else "[FAIL] validation failed")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
