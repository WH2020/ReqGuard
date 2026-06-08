# Technical Detail Archiving

Do not copy every implementation detail into architecture documents. Record only details that affect future changes, verification, contracts, resources, or safety boundaries.

## Must archive

| Detail | Location |
|---|---|
| Module responsibility changes | `modules.md` |
| Interface contract changes | `modules.md` / `decisions.md` |
| Requirement semantics or acceptance changes | `requirements.md` after user confirmation |
| Requirement coverage changes | `traceability.md` |
| Test strategy changes | `traceability.md` / `decisions.md` |
| Key architecture tradeoffs | `decisions.md` |
| Future-maintenance implementation constraints | `modules.md` implementation notes |

## Do not archive

- Local variable explanations.
- Ordinary control flow.
- Details directly obvious from code.
- Temporary debug code.
- Formatting-only changes.
- Experiments without conclusions.

## Profile-specific details

| Profile | Must archive |
|---|---|
| `software-app` | page state machines, API contracts, data models, permissions, security boundaries, compatibility handling |
| `embedded-firmware` | ISR constraints, DMA buffers, RTOS task relationships, locks, register configuration, timing, power |
| `algorithm-model` | input/output definitions, formulas, parameter meaning, complexity, numerical ranges, validation data, metric thresholds |

After code changes, ask:

```text
Did this change introduce a technical constraint future maintainers must know?
```

If yes, update module, traceability, decision, or progress documents.
