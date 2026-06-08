# Enforcement Boundary

ReqGuard separates enforceable controls from best-effort agent behavior.

## Three reliability layers

| Layer | Executor | Reliability | Examples |
|---|---|---|---|
| Hook / CI | PreToolUse, PostToolUse, pre-commit, CI | High | block confirmed requirement edits, update `last_reviewed_commit` |
| Scripts | `validate_ai_workflow.py`, `match_task_context.py` | Medium-high | check IDs, profiles, mappings, JSON validity |
| Agent rules | Skill, AGENTS.md, agent summaries | Best-effort | explain matches, update docs, summarize task |

Only hook/CI rules are truly non-bypassable.

## Hook-owned fields

Treat these `state.json` fields as hook/script-owned:

- `last_reviewed_commit`
- `last_validation_result`
- `last_task_context_hash`
- `last_updated_by`

The agent may propose state changes, but should not hand-edit hook-owned fields.

## PreToolUse candidates

Block these actions when possible:

- Editing confirmed requirements without a confirmed change proposal.
- Editing source code when `task_context.json.blocking=true`.
- Editing source code with no confirmed requirement match.
- Hand-editing `task_context.json` scores or blocking flags.
- Hand-editing hook-owned `state.json` fields.

## PostToolUse candidates

Record facts after tools run:

- Tool name.
- Changed paths.
- Current commit or workspace identifier.
- Validation result.
- Test command and exit code.
- Audit line in `workflow_audit.jsonl`.

## Degraded mode

Without hooks or CI, call the system a best-effort requirements workflow. Do not claim strict enforcement.
