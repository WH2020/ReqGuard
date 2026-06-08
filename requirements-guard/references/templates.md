# ReqGuard Templates

Use these as starter shapes. Add profile-specific fields from `domain-profiles.md`.

## state.json

```json
{
  "workflow_version": "0.1",
  "project_profile": "embedded-firmware",
  "active_profiles": ["embedded-firmware"],
  "active_expert_regions": ["EXP-FW-UART"],
  "phase": "requirements_draft",
  "requirements_version": "REQ-v1",
  "modules_version": "MOD-v1",
  "traceability_version": "TR-v1",
  "task_context_version": "CTX-v1",
  "pending_user_confirmation": true,
  "last_user_confirmed_requirements": null,
  "last_task_alignment": null,
  "last_reviewed_commit": null,
  "last_validation_result": null,
  "last_task_context_hash": null,
  "last_updated_by": null,
  "managed_fields": {
    "hook_owned": [
      "last_reviewed_commit",
      "last_validation_result",
      "last_task_context_hash",
      "last_updated_by"
    ],
    "agent_suggested": [
      "phase",
      "pending_user_confirmation",
      "open_change_proposals"
    ]
  },
  "open_change_proposals": []
}
```

## requirements.md

```markdown
# Requirements

## Metadata

- Project:
- Project profile:
- Active profiles:
- Requirements version: REQ-v1
- Status: draft

## Requirement Index

| ID | Profile | Title | Type | Priority | Status | Related Modules | Related Tests |
|---|---|---|---|---|---|---|---|
| REQ-001 | embedded-firmware | UART DMA receive | functional | high | draft | MOD-001 | TEST-001 |

## REQ-001 UART DMA receive

- Status: draft
- Profile: embedded-firmware
- Type: functional
- Priority: high
- Source: user
- Description:
- Acceptance:
- Verification:
```

## modules.md

```markdown
# Modules

## MOD-001 UART Driver

- Status: planned
- Profile: embedded-firmware
- Covered requirements: REQ-001
- Responsibilities:
- Non-responsibilities:
- Public interfaces:
- Dependencies:
- Tests:
```

## traceability.md

```markdown
# Traceability

| Requirement | Profile | Module | Code | Test | Evidence | Status | Notes |
|---|---|---|---|---|---|---|---|
| REQ-001 | embedded-firmware | MOD-001 | `drivers/uart_driver.c` | TEST-001 | test log | partial | |
```

## expert_regions.md

```markdown
# Expert Regions

## EXP-FW-UART UART DMA receive path

- Profile: embedded-firmware
- Scope: UART DMA receive, circular buffer, ISR index update, overflow handling
- Owned requirements: REQ-001
- Owned modules: MOD-001
- Keywords: uart, dma, isr, buffer, overflow, crc
- Out of scope:
  - Business protocol parsing
- Required tests:
  - TEST-001
```

## task_context.json

```json
{
  "workflow_version": "0.1",
  "generated_by": "match_task_context.py",
  "managed_by": "hook-or-script",
  "raw_user_task": "",
  "task_summary": "",
  "profile_matches": [],
  "expert_region_matches": [],
  "requirement_matches": [],
  "module_matches": [],
  "confidence": {
    "overall": 0.0,
    "profile_confidence": 0.0,
    "expert_region_confidence": 0.0,
    "requirement_confidence": 0.0,
    "module_confidence": 0.0,
    "evidence_quality": "low"
  },
  "risk_flags": [],
  "decision_hint": "clarify",
  "blocking": true,
  "reason": "No task has been matched yet."
}
```
