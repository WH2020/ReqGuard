# Domain Profiles

Use one core ReqGuard workflow with domain-specific profiles.

## Profile selection

`state.json` should include:

```json
{
  "project_profile": "multi-domain",
  "active_profiles": ["software-app", "embedded-firmware", "algorithm-model"]
}
```

Each requirement and module should include a `Profile:` field.

## software-app

Use for PC software, mobile apps, web apps, desktop clients, and host tools.

Required requirement fields:

- Platform
- User Flow
- Actors
- Permissions
- Data
- API Contract
- UI States
- Error States
- Compatibility
- Performance
- Acceptance
- Regression

Required module fields:

- Public API
- State
- Data Model
- Security
- Dependencies
- Failure Modes
- Tests

Recommended gates:

- API schema changes require contract tests.
- Data model changes require migration or compatibility notes.
- Permission changes require security notes.
- Key user-flow changes require regression tests.

## embedded-firmware

Use for MCU/SoC firmware, drivers, communication protocols, RTOS, and board support.

Required requirement fields:

- MCU/SoC
- Peripheral
- Pins
- Clock
- Timing
- RAM Budget
- Flash Budget
- ISR Constraints
- DMA Constraints
- RTOS Constraints
- Power
- Failure Recovery
- Acceptance
- Verification

Required module fields:

- ISR Responsibilities
- DMA Strategy
- RTOS Interaction
- Shared Data
- Critical Sections
- Register Configuration
- Hardware Dependencies
- Resource Budget
- Timing Constraints
- Failure Modes
- Tests

Recommended gates:

- ISR changes require ISR constraints or a no-impact note.
- DMA buffer changes require resource-budget updates.
- RTOS queue/task changes require task-relationship updates.
- Register changes require hardware-dependency notes.

## algorithm-model

Use for algorithms, signal processing, model validation, inference logic, and data algorithms.

Required requirement fields:

- Input
- Output
- Dataset
- Metric
- Accuracy Target
- Latency Target
- Complexity
- Numerical Range
- Edge Cases
- Baseline
- Acceptance
- Verification

Required module fields:

- Algorithm
- Inputs
- Outputs
- Parameters
- Assumptions
- Complexity
- Numerical Constraints
- Dependencies
- Validation Dataset
- Benchmark
- Failure Modes
- Tests

Recommended gates:

- Parameter changes require parameter notes or benchmark updates.
- Data processing changes require dataset version or input-assumption updates.
- Metric changes require metric-definition updates.
- Core algorithm/model changes require validation evidence.
