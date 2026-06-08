---
name: requirements-guard
description: Requirements-gated AI engineering workflow for AI-assisted software, firmware, and algorithm development. Use when Codex must work from confirmed requirements, maintain module and traceability documents, align each task against requirement/module/domain-profile networks before implementation, control requirement changes, or distinguish hook-enforced rules from best-effort agent rules. Triggers include ReqGuard, requirements guard, requirement-driven development, spec-driven development, task alignment gate, traceability matrix, domain profiles, hook enforcement, or requests to prevent AI coding drift.
---

# Requirements Guard

ReqGuard is a requirements-gated engineering workflow for AI agents. Use it to keep work aligned with confirmed requirements, module boundaries, traceability evidence, domain profiles, and hook-aware enforcement.

## Reliability boundary

Do not overstate the workflow's strictness.

- Hook, CI, and deterministic scripts are enforceable.
- Validation scripts are auditable and repeatable.
- Agent-written summaries, status, and documentation updates are best-effort until validated.
- Treat hook-owned fields in `state.json` as read-only for the agent.
- Treat `task_context.json` scores and blocking flags as script-owned; do not hand-edit them.

Read `references/enforcement-boundary.md` when the task involves hooks, CI, state trust, or claims of strict enforcement.

## Project layout

Prefer `docs/reqguard/`; also accept existing `docs/ai-workflow/` projects.

```text
docs/reqguard/
  requirements.md
  modules.md
  traceability.md
  decisions.md
  progress.md
  state.json
  task_context.json
  changes/
scripts/
  validate_ai_workflow.py
  match_task_context.py
```

## Core workflow

1. Load project instructions and ReqGuard state.
2. Read `state.json`, `requirements.md`, `modules.md`, `traceability.md`, and `progress.md` if present.
3. Load active domain profiles from `state.json.active_profiles`.
4. Before implementation, run task alignment:
   - Use `scripts/match_task_context.py` if available in the project.
   - Otherwise use this skill's bundled `scripts/match_task_context.py`.
5. State the task in one sentence.
6. Report profile, requirement, and module matches.
7. Implement only against confirmed requirements.
8. For requirement semantic changes, create a change proposal and wait for user confirmation.
9. After meaningful code, interface, test, or design changes, update module and traceability docs.
10. Run validation:
   - Use project `scripts/validate_ai_workflow.py` if available.
   - Otherwise use this skill's bundled `scripts/validate_ai_workflow.py`.

## Task alignment output

Before code changes, produce a short preflight block:

```markdown
Task: one-sentence summary.

Matches:
- Profile: embedded-firmware, score=0.93
- Requirement: REQ-001 UART DMA receive, score=0.86, status=confirmed
- Module: MOD-001 UART Driver, score=0.81

Decision:
- proceed / clarify / create requirement / create change proposal / blocked

Boundary:
- This task changes ...
- This task does not change ...
```

If `task_context.json` says `blocking=true`, do not implement. Explain the blocking reason and ask for user input or requirement confirmation.

## Domain profiles

Use one core workflow with domain profiles.

- `software-app`: PC software, mobile apps, web apps, desktop clients, host tools.
- `embedded-firmware`: MCU/SoC firmware, drivers, communication protocols, RTOS, board support.
- `algorithm-model`: algorithms, signal processing, model validation, inference logic, data algorithms.

Read `references/domain-profiles.md` when requirements or modules involve platform-specific fields, firmware timing/resources, or algorithm validation.

## Requirement and module updates

Requirement changes:

- Draft new requirements freely.
- Do not silently edit confirmed requirements.
- If semantics, acceptance criteria, priority, or scope changes, create a change proposal first.
- User confirmation is required before confirmed requirements change.

Module and traceability changes:

- Update `modules.md` when responsibilities, non-responsibilities, public interfaces, dependencies, resources, timing, data model, or algorithm assumptions change.
- Update `traceability.md` when requirement-module-code-test-evidence mappings change.
- Record key design tradeoffs in `decisions.md`.
- Do not copy every implementation detail into architecture docs. Read `references/technical-detail-archiving.md` for what must be recorded.

## Templates and references

- Read `references/templates.md` for starter document shapes.
- Read `references/task-alignment.md` for scoring fields and thresholds.
- Read `references/domain-profiles.md` for software, firmware, and algorithm profile fields.
- Read `references/enforcement-boundary.md` for hook/CI vs best-effort boundaries.
- Read `references/technical-detail-archiving.md` before deciding whether to document implementation details.

## Scripts

Bundled scripts are dependency-free Python utilities:

```bash
python requirements-guard/scripts/match_task_context.py --root . --task "implement UART DMA overflow handling"
python requirements-guard/scripts/validate_ai_workflow.py --root .
```

They support both `docs/reqguard/` and `docs/ai-workflow/`.
