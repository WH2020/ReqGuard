# Expert Regions

Expert regions make ReqGuard more precise than broad domain profiles. A profile says "embedded firmware"; an expert region says "UART DMA receive path".

## Match order

```text
task -> profile -> expert_region -> requirement -> module -> test
```

## expert_regions.md

Create `docs/reqguard/expert_regions.md` or `docs/ai-workflow/expert_regions.md`.

```markdown
# Expert Regions

## EXP-FW-UART UART DMA receive path

- Profile: embedded-firmware
- Scope: UART DMA receive, circular buffer, ISR index update, overflow handling
- Owned requirements: REQ-001, REQ-002
- Owned modules: MOD-001
- Keywords: uart, dma, isr, buffer, overflow, crc
- Out of scope:
  - Business protocol parsing
  - UI display
- Required tests:
  - TEST-001
```

## Confidence model

`task_context.json` should include:

```json
{
  "confidence": {
    "overall": 0.82,
    "profile_confidence": 0.93,
    "expert_region_confidence": 0.88,
    "requirement_confidence": 0.79,
    "module_confidence": 0.81,
    "evidence_quality": "medium"
  }
}
```

Evidence quality:

- `high`: profile, expert region, confirmed requirement, module, and test evidence all match.
- `medium`: profile, requirement, and module match, but test evidence or expert region is weak.
- `low`: only profile or free-text similarity matches.

## OOD detection

Use `out_of_distribution_task` when no active profile or expert region fits the task.

```json
{
  "type": "out_of_distribution_task",
  "message": "Task does not fit any active expert region."
}
```

Do not implement OOD tasks directly. Create a draft requirement, propose a new expert region, or ask for clarification.

## Execution protocol

Before implementation, the agent should produce:

```markdown
## Execution Protocol

- Target profile:
- Target expert region:
- Target requirement:
- Target module:
- Allowed files:
- Forbidden changes:
- Required tests:
- Validation evidence:
- Rollback risk:
```

The protocol is more specific than a plan. It defines the allowed boundary for the implementation.
