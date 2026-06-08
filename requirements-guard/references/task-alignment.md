# Task Alignment

Task alignment prevents the agent from implementing outside confirmed requirements and module boundaries.

## Match order

1. Match domain profile.
2. Match confirmed requirements.
3. Match modules.
4. Check traceability and test evidence.
5. Decide: proceed, clarify, create requirement, create change proposal, or block.

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
- Requirement and module profiles conflict without user-confirmed cross-domain scope.
- `task_context.json.blocking=true`.

## Required agent preflight

```markdown
Task: one-sentence summary.

Matches:
- Profile: ...
- Requirement: ...
- Module: ...

Decision:
- ...

Boundary:
- This task changes ...
- This task does not change ...
```
