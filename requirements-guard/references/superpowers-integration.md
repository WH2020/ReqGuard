# Superpowers Integration

ReqGuard owns requirement truth, task alignment, traceability, and hook-aware state.
Superpowers-style discipline improves how implementation proceeds after ReqGuard allows it.

## Borrowed rules

Use these as execution discipline, not as a replacement for requirements:

- **Planning**: implementation work should have a concrete protocol: target requirement, module, files, tests, evidence.
- **TDD / evidence-first**: new behavior and bug fixes need a failing or baseline check before code changes when practical.
- **Debugging**: bug, performance, timing, and verification failures require root-cause investigation before fixes.
- **Verification**: do not claim completion without fresh validation evidence.
- **Review**: for major changes, run a requirement-compliance review before code-quality review.

## Required process

`task_context.json.required_process` should be one of:

- `implementation`: normal feature or refactor within confirmed scope.
- `debugging`: bug, failure, timing, performance, crash, data mismatch, or unexpected behavior.
- `review`: review, audit, pre-merge, or compliance-only task.
- `requirement_change`: new requirement, semantic requirement edit, or OOD task.

## Debugging protocol

For `debugging`, do not guess fixes. Use:

```text
symptom -> reproduction -> evidence -> root-cause hypothesis -> minimal test -> fix -> regression evidence
```

For firmware, evidence may be logs, register snapshots, trace capture, waveform timing, HIL output, or RTOS metrics.
For algorithms, evidence may be golden data, metric deltas, residuals, confusion matrix changes, or benchmark output.

## Completion gate

Before reporting a task complete, verify:

- `task_alignment=true`
- `workflow_validation=true`
- `project_tests=true`
- `traceability_updated=true`
- `evidence_recorded=true`

These fields are script/hook owned when possible. Agent-written completion statements are best-effort until the gate is validated.

## Review order

For major tasks:

1. Requirement compliance review: requirement IDs, module boundary, expert region, OOD, traceability.
2. Engineering quality review: correctness, tests, performance, maintainability, resources, concurrency, realtime risk.

Do not start code-quality review until requirement compliance passes.
