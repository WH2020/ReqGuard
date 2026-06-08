# ReqGuard

ReqGuard is a requirements-gated AI engineering workflow packaged as a Codex skill.

It helps AI agents work from confirmed requirements, align tasks against domain profiles and expert regions, maintain module and traceability documents, report confidence, detect out-of-distribution tasks, and distinguish hook/CI-enforced controls from best-effort agent behavior.

## Skill

The skill lives in:

```text
requirements-guard/
```

Use the skill when an AI agent must:

- implement only against confirmed requirements
- run a task alignment gate before code changes
- route each task through active expert regions before implementation
- report confidence and block out-of-distribution work until clarified
- maintain requirement-module-code-test traceability
- support software, embedded firmware, and algorithm domain profiles
- separate hook-enforced rules from best-effort agent rules

## Scripts

```bash
python requirements-guard/scripts/match_task_context.py --root . --task "implement UART DMA overflow handling"
python requirements-guard/scripts/validate_ai_workflow.py --root .
```

Both scripts support `docs/reqguard/` and `docs/ai-workflow/`.
