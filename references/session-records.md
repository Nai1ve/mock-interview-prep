# Local recording and recovery

Use Python 3 and the bundled `scripts/session.py` (standard library; macOS/Linux). Resolve its absolute path from the skill directory. No search API keys or database are required. On unsupported systems/file tools, disclose the limitation rather than claim persistence.

Default session directory: `~/Documents/interview-records/<date-role-random-id>/`, outside the skill checkout. Use a sanitized role slug without names/contact details; use a unique suffix. Local files contain sensitive career information: do not upload, commit, or include private records in examples. Files are created mode 0600 and session directory 0700. Avoid printing full records in terminal output unless necessary. Keep input JSON files in a private temporary directory or session directory with the same permissions; shell arguments should contain paths, not resume/answer text. Use file tools to write JSON, not interpolated shell commands.

## Plan

Write a UTF-8 JSON plan containing:

For new sessions use the complete synthetic schema-v2 plan in [backend-plan.json](../examples/backend-plan.json) as a structural example; replace the focus, projects, resume claims, topics and time budget from the actual inputs. It demonstrates backend practice against a full-stack role, not universal Redis/database requirements.

Required additions to the old plan format:

- `schema_version: 2`.
- `practice_scope`: `objective`, `included_domains`, `excluded_domains`.
- `projects`: stable `id`, `name`, `priority`; keep only projects relevant to this session's focus.
- `resume_map`: distinct `claim_id`, `resume_evidence`, and `project_id` for project-specific claims. Avoid umbrella technology claims.
- `topics`: stable `id`, `name`, `domain`, `basis`, `required` boolean, `reserve_minutes`, `target_depth` (touched/basic/mechanism/boundary). Required topics have positive protected sampling time. Sum of required reserves cannot exceed total time; they are part of existing module budgets, not additional time.
- `preparation_research`: concise statement of actual preparation research/limitations; a source added after finish is not preparation.

Choose required topics from actual focus/resume/JD. Reserves protect an opportunity to sample, not a guarantee of mastery. A short session should have fewer priority topics with credible time allowances, not tiny reserves to game coverage.

Fill resume_map and any jd_requirements with actual evidence and priorities. For wall_clock, include timezone-aware ISO `deadline` and explain whether waiting is counted. Question counts are advisory. Initialize:

```sh
python3 /absolute/skill/scripts/session.py init --dir /absolute/private/session --plan /absolute/private/plan.json
```

## Events

Write an event JSON file, then call `append --dir SESSION --event EVENT_FILE`. Persist before asking the next question. The script adds sequence and UTC timestamp, serializes concurrent writers, and atomically replaces the log. `events.jsonl` and `plan.json` are authoritative; `session.json` and `sources.json` are rebuildable projections.

- **question**: `id`, `text`, `module_id`, `domain`, `question_type`, `evidence_goal`, and `resume_claim_ids` or `jd_requirement`. Follow-ups also set `parent_id`. IDs must be unique; record only questions actually asked. Do not pre-log future questions.
- **answer**: `question_id`, `text` (candidate's actual full text, not a model rewrite).
- **assessment**: `question_id`, `status` (untested/partial/demonstrated/gap/uncertain), `evidence`, `decision` (deepen/branch/move_on/end), `reason`. Add `gaps`, applicable scores, and proposed next evidence as useful. Candidate-facing feedback waits until finish. Assessments can be refined after finish without advancing time.
- **source**: `id`, `query`, `title`, `url`, `retrieved_at`, `version`, `claim`, `verified` (boolean). Add failed verification detail if relevant. Reusing a source ID updates its projection while preserving event history.
- **replan**: complete revised `plan` plus `reason`; preserve module IDs, total budget, clock mode and deadline. This redistributes time, not an implicit extension. For a user-authorized additional interview budget, finish the old session and start a linked continuation session.
- **finish**: `reason`, optionally uncovered priorities and timing overrun. May finish early on user request, including with a pending unanswered question; review must acknowledge it.

Any time-advancing event must include a valid `module_id` and cumulative, nondecreasing `elapsed_minutes`. This enables per-module accounting and preserves overruns. Use honest active estimates or measured elapsed wall-clock time as disclosed. Bookkeeping and final reports cannot advance assessment time after finish. Strict wall-clock deadlines block new questions even if recorded elapsed minutes are stale. The script does not run an autonomous timer or interrupt candidate input.

Example follow-up event:

```json
{"type":"question","id":"Q1.1","parent_id":"Q1","text":"What evidence ruled out lock contention?","module_id":"projects","domain":"database","question_type":"project","evidence_goal":"Validate diagnosis rather than tool-name recall","resume_claim_ids":["R2"]}
```

## Resume

Call `show --dir SESSION` before resuming. It replays events and repairs projections. Inspect pending_question_ids, coverage, remaining time, previous assessments and source verification. Do not re-ask an answered question because a snapshot was stale. Corrupt history fails explicitly; do not silently discard it. Source absence means not researched, not verified.

## Final report

After finish, write a review JSON with `answers` keyed by **every asked question ID**, including follow-ups. Each entry requires nonempty `critique`, `gaps`, and `reference_answer`. Also supply nonempty Markdown strings `summary`, `study_plan`, `retest_questions`, `reverse_question_suggestions`. Use “not answered/not assessed” where appropriate; never invent an answer.

```sh
python3 /absolute/skill/scripts/session.py report --dir /absolute/private/session --review /absolute/private/review.json
```

The script rejects missing question reviews and creates report.md with timing/coverage, question/answer ledger, sources, complete per-question reviews, study plan, retest and optional-use reverse-question suggestions. It can check completeness of fields, not technical truth or answer depth: inspect the rendered Markdown for substantive full answers, evidence-based judgments, source support and marked unknown project facts before delivery. Link the report in the final response; summarize key gaps without pasting private logs unnecessarily.

## Scope and depth checks (schema v2)

Every question additionally requires `topic_id`, `evidence_kind` (resume_actual/hypothetical/fundamentals), `selection_reason`, and positive `expected_answer_minutes` including question overhead. `project_id` is required for actual experience questions; a linked resume claim must belong to that project. Domain must match the registered in-scope topic. For follow-ups, assess the parent first. No fixed follow-up count is enforced.

Assessments additionally require `observed_depth`, `depth_evidence`, and `remaining_unknowns` (use an explicit “none observed within this scope” if appropriate). Depth measures evidence independently of correctness status. A correct basic answer cannot automatically meet a mechanism target. Do not award deeper evidence just because the interviewer asked a deep question.

Sources additionally require `phase` (preparation/live/review); after finish only review sources are accepted. Replans cannot remove protected topics, reduce sampling reserves or lower target depths unless `user_scope_change` quotes an actual user request. Scope cannot silently expand or contract. Do not fabricate user authorization or relabel topics to bypass checks.

Run `python3 /absolute/skill/scripts/session.py check --dir SESSION` before selecting each next question. It returns scoped topic depth, unsampled priorities, protected time and actual/hypothetical project evidence without printing candidate answers. The next question cannot consume the sampling reserves of other untested required topics. Important untouched projects and insufficient depth remain visible warnings for the interviewer to resolve, not evidence of failure by the candidate.

Old-schema records remain readable and resumable without migration. `check` labels their limited granularity. Do not silently rewrite prior logs or claim their old tags prove new-schema coverage.
