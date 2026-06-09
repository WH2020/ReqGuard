# Task Alignment

Task alignment prevents the agent from implementing outside confirmed requirements and module boundaries.

## Match order

1. Match domain profile.
2. Match expert region if `expert_regions.md` exists.
3. Match confirmed requirements.
4. Match modules.
5. Check traceability and test evidence.
6. Decide: proceed, clarify, create requirement, create change proposal, or block.

## Scoring

Recommended final score:

```text
final_score =
  0.35 * semantic_similarity
+ 0.20 * keyword_overlap
+ 0.20 * file_or_module_path_match
+ 0.15 * profile_match
+ 0.10 * current_state_weight
```

When the user task and candidate text do not include concrete file paths, redistribute the path weight to keyword/profile-sensitive matching. The bundled matcher uses deterministic text similarity and profile heuristics. Production systems may replace it with embeddings, but the output contract should remain stable.

## Thresholds

| Score | Decision |
|---|---|
| `>= 0.75` | High match, proceed if requirement is confirmed |
| `0.50 - 0.75` | Clarify or ask for boundary confirmation |
| `< 0.50` | Do not implement; create or clarify requirement |

Always block implementation when:

- Best requirement is draft, changed, deprecated, or missing.
- No active profile matches.
- No active expert region matches when expert regions are defined.
- Requirement and module profiles conflict without user-confirmed cross-domain scope.
- `task_context.json.blocking=true`.
- `out_of_distribution_task` is present.

## Required agent preflight

```markdown
Task: one-sentence summary.

Matches:
- Profile: ...
- Expert region: ...
- Requirement: ...
- Module: ...

Confidence:
- overall=...
- evidence_quality=...

Process:
- required_process=...
- required_verification=...

Decision:
- ...

Boundary:
- This task changes ...
- This task does not change ...
```

## Completion gate

Before reporting completion, the task must have:

- `completion_gate.task_alignment=true`
- `completion_gate.workflow_validation=true`
- `completion_gate.project_tests=true`
- `completion_gate.traceability_updated=true`
- `completion_gate.evidence_recorded=true`

If any item is false, report partial progress and missing evidence instead of claiming completion.

## Execution protocol

For implementation tasks, add:

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
