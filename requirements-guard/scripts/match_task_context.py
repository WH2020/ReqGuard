#!/usr/bin/env python3
"""Generate ReqGuard task_context.json from a user task.

This dependency-free matcher is intentionally conservative. It uses deterministic
text similarity and profile heuristics; projects may replace it with embeddings
as long as the JSON contract remains compatible.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


VALID_PROFILES = ("software-app", "embedded-firmware", "algorithm-model")
PROFILE_KEYWORDS = {
    "software-app": {
        "ui", "api", "auth", "login", "screen", "page", "view", "android", "ios",
        "windows", "desktop", "web", "permission", "database", "migration", "state",
        "cache", "router", "endpoint", "frontend", "backend",
    },
    "embedded-firmware": {
        "mcu", "soc", "uart", "spi", "i2c", "can", "dma", "isr", "interrupt",
        "rtos", "timer", "gpio", "adc", "register", "flash", "ram", "power",
        "firmware", "driver", "protocol", "buffer", "crc", "hal",
    },
    "algorithm-model": {
        "algorithm", "model", "signal", "filter", "fft", "peak", "dataset",
        "metric", "accuracy", "precision", "recall", "latency", "complexity",
        "parameter", "benchmark", "inference", "validation", "numeric",
    },
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


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


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


def title_from_block(block: str, item_id: str) -> str:
    first_line = block.splitlines()[0] if block else item_id
    return re.sub(rf"^##\s+{re.escape(item_id)}\s*", "", first_line).strip() or item_id


def normalize(text: str) -> str:
    return text.lower().replace("_", " ").replace("-", " ")


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]", normalize(text)))


def char_ngrams(text: str, min_n: int = 2, max_n: int = 4) -> Counter[str]:
    compact = re.sub(r"\s+", " ", normalize(text)).strip()
    counts: Counter[str] = Counter()
    for n in range(min_n, max_n + 1):
        for idx in range(0, max(0, len(compact) - n + 1)):
            counts[compact[idx : idx + n]] += 1
    return counts


def cosine(a: Counter[str], b: Counter[str]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(value * b.get(key, 0) for key, value in a.items())
    norm_a = math.sqrt(sum(value * value for value in a.values()))
    norm_b = math.sqrt(sum(value * value for value in b.values()))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def containment(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def profile_score(task: str, profile: str) -> tuple[float, list[str]]:
    task_tokens = tokens(task)
    keywords = PROFILE_KEYWORDS.get(profile, set())
    hits = sorted(task_tokens & keywords)
    score = min(1.0, len(hits) / 3.0)
    reasons = [f"matched profile keyword: {hit}" for hit in hits[:5]]
    return score, reasons


def path_score(task: str, candidate: str) -> float:
    task_items = set(re.findall(r"[\w./\\-]+\.(?:c|h|cpp|hpp|py|ts|tsx|js|jsx|java|kt|swift|md)", task.lower()))
    candidate_items = set(re.findall(r"[\w./\\-]+\.(?:c|h|cpp|hpp|py|ts|tsx|js|jsx|java|kt|swift|md)", candidate.lower()))
    if not task_items or not candidate_items:
        return 0.0
    return len(task_items & candidate_items) / len(task_items | candidate_items)


def has_path_hint(task: str, candidate: str) -> bool:
    pattern = r"[\w./\\-]+\.(?:c|h|cpp|hpp|py|ts|tsx|js|jsx|java|kt|swift|md)"
    return bool(re.search(pattern, task.lower()) and re.search(pattern, candidate.lower()))


def current_state_weight(block: str) -> float:
    status = (field_value(block, "Status") or "").lower()
    if status == "confirmed":
        return 1.0
    if status in {"implemented", "verified"}:
        return 0.9
    if status in {"draft", "changed"}:
        return 0.2
    if status == "deprecated":
        return 0.0
    return 0.5


def score_candidate(task: str, candidate: str, profile_match: float) -> dict:
    semantic = cosine(char_ngrams(task), char_ngrams(candidate))
    task_tokens = tokens(task)
    candidate_tokens = tokens(candidate)
    profile_keyword = 0.0
    for keywords in PROFILE_KEYWORDS.values():
        task_profile_hits = task_tokens & keywords
        if task_profile_hits:
            profile_keyword = max(profile_keyword, len(task_profile_hits & candidate_tokens) / len(task_profile_hits))
    keyword = max(jaccard(task_tokens, candidate_tokens), containment(task_tokens, candidate_tokens), profile_keyword)
    path = path_score(task, candidate)
    state = current_state_weight(candidate)
    if has_path_hint(task, candidate):
        final = 0.35 * semantic + 0.20 * keyword + 0.20 * path + 0.15 * profile_match + 0.10 * state
    else:
        final = 0.35 * semantic + 0.40 * keyword + 0.15 * profile_match + 0.10 * state
    return {
        "score": round(final, 4),
        "semantic_similarity": round(semantic, 4),
        "keyword_overlap": round(keyword, 4),
        "file_or_module_path_match": round(path, 4),
        "profile_match": round(profile_match, 4),
        "current_state_weight": round(state, 4),
    }


def top_matches(task: str, blocks: dict[str, str], active_profiles: list[str], limit: int) -> list[dict]:
    matches: list[dict] = []
    profile_scores = {profile: profile_score(task, profile)[0] for profile in active_profiles}
    default_profile_score = max(profile_scores.values(), default=0.0)
    for item_id, block in blocks.items():
        profile = field_value(block, "Profile")
        p_score = profile_scores.get(profile, default_profile_score if not profile else 0.0)
        scores = score_candidate(task, block, p_score)
        title = title_from_block(block, item_id)
        status = field_value(block, "Status") or ""
        reasons = []
        if profile:
            reasons.append(f"profile={profile}")
        if scores["semantic_similarity"] > 0:
            reasons.append(f"semantic_similarity={scores['semantic_similarity']}")
        if scores["keyword_overlap"] > 0:
            reasons.append(f"keyword_overlap={scores['keyword_overlap']}")
        matches.append({
            "id": item_id,
            "title": title,
            "profile": profile,
            "status": status,
            **scores,
            "match_reasons": reasons,
        })
    return sorted(matches, key=lambda item: item["score"], reverse=True)[:limit]


def evidence_quality(requirements: list[dict], modules: list[dict], regions: list[dict], profiles: list[dict], has_regions: bool) -> str:
    profile_score_value = profiles[0]["score"] if profiles else 0.0
    region_score_value = regions[0]["score"] if regions else (1.0 if not has_regions else 0.0)
    req_score_value = requirements[0]["score"] if requirements else 0.0
    mod_score_value = modules[0]["score"] if modules else 0.0
    if profile_score_value >= 0.75 and region_score_value >= 0.75 and req_score_value >= 0.75 and mod_score_value >= 0.75:
        return "high"
    if profile_score_value >= 0.5 and req_score_value >= 0.5 and mod_score_value >= 0.5:
        return "medium"
    return "low"


def confidence(requirements: list[dict], modules: list[dict], regions: list[dict], profiles: list[dict], has_regions: bool) -> dict:
    profile_confidence = profiles[0]["score"] if profiles else 0.0
    expert_region_confidence = regions[0]["score"] if regions else (1.0 if not has_regions else 0.0)
    requirement_confidence = requirements[0]["score"] if requirements else 0.0
    module_confidence = modules[0]["score"] if modules else 0.0
    components = [profile_confidence, requirement_confidence, module_confidence]
    if has_regions:
        components.append(expert_region_confidence)
    overall = sum(components) / len(components) if components else 0.0
    return {
        "overall": round(overall, 4),
        "profile_confidence": round(profile_confidence, 4),
        "expert_region_confidence": round(expert_region_confidence, 4),
        "requirement_confidence": round(requirement_confidence, 4),
        "module_confidence": round(module_confidence, 4),
        "evidence_quality": evidence_quality(requirements, modules, regions, profiles, has_regions),
    }


def decision(requirements: list[dict], modules: list[dict], regions: list[dict], profiles: list[dict], has_regions: bool) -> tuple[str, bool, str, list[dict]]:
    risks: list[dict] = []
    best_profile = profiles[0] if profiles else None
    best_region = regions[0] if regions else None
    best_req = requirements[0] if requirements else None
    best_mod = modules[0] if modules else None

    if not best_profile or best_profile["score"] < 0.5:
        risks.append({"type": "low_profile_match", "message": "No active domain profile matched the task."})
        risks.append({"type": "out_of_distribution_task", "message": "Task does not fit any active domain profile."})
        return "create_requirement", True, "Task is outside active domain profiles.", risks

    if has_regions and (not best_region or best_region["score"] < 0.5):
        risks.append({"type": "out_of_distribution_task", "message": "Task does not fit any active expert region."})
        return "create_requirement", True, "Task is outside active expert regions.", risks

    if not best_req:
        risks.append({"type": "missing_requirement", "message": "No requirement candidates found."})
        return "create_requirement", True, "No requirement candidates found.", risks

    if (best_req.get("status") or "").lower() != "confirmed":
        risks.append({"type": "unconfirmed_requirement", "message": f"Best requirement {best_req['id']} is not confirmed."})
        return "confirm_requirement", True, "Best requirement is not confirmed.", risks

    if best_req["score"] < 0.5:
        risks.append({"type": "low_requirement_match", "message": "Best confirmed requirement score is below 0.50."})
        return "clarify", True, "Low requirement match.", risks

    if not best_mod:
        risks.append({"type": "missing_module", "message": "No module candidates found."})
        return "clarify", True, "No module candidates found.", risks

    if best_mod["score"] < 0.5:
        risks.append({"type": "low_module_match", "message": "Best module score is below 0.50."})
        return "clarify", True, "Low module match.", risks

    req_profile = best_req.get("profile")
    mod_profile = best_mod.get("profile")
    if req_profile and mod_profile and req_profile != mod_profile:
        risks.append({"type": "profile_conflict", "message": f"{best_req['id']} profile {req_profile} differs from {best_mod['id']} profile {mod_profile}."})
        return "clarify", True, "Requirement and module profiles conflict.", risks

    if has_regions and best_region:
        region_profile = best_region.get("profile")
        if region_profile and req_profile and region_profile != req_profile:
            risks.append({"type": "expert_region_conflict", "message": f"{best_region['id']} profile {region_profile} differs from {best_req['id']} profile {req_profile}."})
            return "clarify", True, "Expert region and requirement profiles conflict.", risks

    if best_req["score"] < 0.75 or best_mod["score"] < 0.75:
        risks.append({"type": "medium_match", "message": "Best matches are below high-confidence threshold."})
        return "clarify", False, "Medium confidence match; ask for boundary confirmation.", risks

    return "proceed", False, "Task matches a confirmed requirement and compatible module.", risks


def summarize_task(task: str) -> str:
    cleaned = " ".join(task.strip().split())
    return cleaned[:180]


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate ReqGuard task_context.json.")
    parser.add_argument("--root", default=".", help="Project root. Defaults to current directory.")
    parser.add_argument("--task", required=True, help="Raw user task text.")
    parser.add_argument("--output", help="Output path. Defaults to docs/reqguard/task_context.json or docs/ai-workflow/task_context.json.")
    parser.add_argument("--limit", type=int, default=3, help="Top matches per category.")
    parser.add_argument("--print", action="store_true", help="Print JSON to stdout too.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    docs = find_docs_dir(root)
    if not docs:
        print("missing docs/reqguard or docs/ai-workflow", file=sys.stderr)
        return 1

    state = read_json(docs / "state.json")
    active_profiles = [profile for profile in state.get("active_profiles", []) if profile in VALID_PROFILES]
    if not active_profiles:
        active_profiles = list(VALID_PROFILES)

    task = args.task
    profile_matches = []
    for profile in active_profiles:
        score, reasons = profile_score(task, profile)
        profile_matches.append({
            "profile": profile,
            "score": round(score, 4),
            "match_reasons": reasons,
        })
    profile_matches.sort(key=lambda item: item["score"], reverse=True)

    req_blocks = section_blocks(read_text(docs / "requirements.md"), "REQ")
    mod_blocks = section_blocks(read_text(docs / "modules.md"), "MOD")
    all_region_blocks = section_blocks(read_text(docs / "expert_regions.md"), "EXP")
    active_regions = set(state.get("active_expert_regions", []))
    region_blocks = all_region_blocks
    if active_regions:
        region_blocks = {key: value for key, value in all_region_blocks.items() if key in active_regions}
    has_regions = bool(all_region_blocks) or bool(active_regions)
    region_matches = top_matches(task, region_blocks, active_profiles, args.limit) if has_regions else []
    req_matches = top_matches(task, req_blocks, active_profiles, args.limit)
    mod_matches = top_matches(task, mod_blocks, active_profiles, args.limit)
    hint, blocking, reason, risks = decision(req_matches, mod_matches, region_matches, profile_matches, has_regions)
    confidence_result = confidence(req_matches, mod_matches, region_matches, profile_matches, has_regions)

    generated_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    result = {
        "workflow_version": "0.1",
        "generated_by": "match_task_context.py",
        "managed_by": "hook-or-script",
        "generated_at": generated_at,
        "raw_user_task": task,
        "task_summary": summarize_task(task),
        "profile_matches": profile_matches[: args.limit],
        "expert_region_matches": region_matches,
        "requirement_matches": req_matches,
        "module_matches": mod_matches,
        "confidence": confidence_result,
        "risk_flags": risks,
        "decision_hint": hint,
        "required_agent_action": "state_task_summary_and_boundary",
        "blocking": blocking,
        "reason": reason,
    }
    result["content_hash"] = hashlib.sha256(
        json.dumps(result, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()

    output = Path(args.output).resolve() if args.output else docs / "task_context.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.print:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Wrote {output}")
        print(f"Decision: {hint}; blocking={blocking}; reason={reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
