# Local recording and recovery

Use Python 3 and the bundled `scripts/session.py` (standard library; macOS/Linux). Resolve its absolute path from the skill directory. No search API keys or database are required. On unsupported systems/file tools, disclose the limitation rather than claim persistence.

Default session directory: `~/Documents/interview-records/<date-role-random-id>/`, outside the skill checkout. Use a sanitized role slug without names/contact details; use a unique suffix. Local files contain sensitive career information: do not upload, commit, or include private records in examples. Files are created mode 0600 and session directory 0700. Avoid printing full records in terminal output unless necessary. Keep input JSON files in a private temporary directory or session directory with the same permissions; shell arguments should contain paths, not resume/answer text. Use file tools to write JSON, not interpolated shell commands.

## Plan

Write a UTF-8 JSON plan containing:

```json
{
  "role": "Backend-oriented full-stack engineer",
  "stage": "technical",
  "duration_minutes": 60,
  "timing_mode": "active_estimate",
  "timing_basis": "Estimated spoken answer + questioning time; offline waiting and research excluded",
  "modules": [
    {"id":"experience","name":"Experience alignment","minutes":6,"domains":["ownership"]},
    {"id":"projects","name":"Resume projects","minutes":24,"domains":["backend","frontend"]},
    {"id":"foundations","name":"Foundations","minutes":15,"domains":["runtime","database"]},
    {"id":"scenario","name":"Scenario/debugging","minutes":15,"domains":["systems"]}
  ],
  "resume_map": [],
  "jd_requirements": [],
  "expected_main_questions": "7–10, including follow-up time"
}
```

Fill resume_map with the actual evidence map and jd_requirements with prioritized requirements; empty arrays above illustrate schema only. For wall_clock, include timezone-aware ISO `deadline` and explain whether waiting is counted. Question counts are advisory. Initialize:

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
