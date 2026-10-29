# Mock Interview Prep

A resume- and JD-grounded mock interview skill with a disclosed time budget, adaptive probing, model-native research and private local records. This fork evolves the original general interview-preparation scaffold into a simulation-only workflow.

## Use

Supply your actual resume, JD, today's practice direction, interview stage and duration, for example:

> 用 mock-interview-prep 今天重点练后端，模拟一场 60 分钟技术面试。简历和全栈 JD 如下；本次不单独考前端。请先给出时间分配与能力覆盖计划，面试中不要讲答案，结束后给完整参考答案和薄弱点报告。

The skill reads the entire available resume, maps claims to role requirements, assigns time across relevant domains and question types, then asks one question at a time. Follow-up depth depends on evidence and remaining time, not a fixed count. Question counts are estimates, not fixed quotas. A frontend-heavy resume does not erase backend or other JD requirements. The same planning applies to nontechnical roles.

Only simulation mode is provided. No mid-interview coaching or pass-score retry loop. All assessment time is used for questioning; suggested questions for the employer appear only in the final report, outside the budget.

## Search

Uses the running model's web search and page-reading tools when available. No dedicated search subscription or provider key is required by this skill. Search/current verification is unavailable when the host has no such tools; the skill must disclose this. Official documentation and versioned release notes take priority. Resume text and private answer logs are not sent as search queries.

## Records and timing

Python 3 on macOS/Linux supports the bundled local ledger. No database, network client or model SDK is needed. Default records live outside this repository under `~/Documents/interview-records/`, in private session folders. The full instructions and schema are in [session-records](references/session-records.md).

Asynchronous text defaults to explicitly estimated active interview time. Offline waiting/research is excluded. Strict wall-clock mode requires reliable clock access and a recorded deadline; the script blocks new questions after that deadline, but cannot interrupt a running answer. Reports distinguish measured and estimated timing.

The final report contains actual question/answer records, all main and follow-up question reviews, complete reference answers, gaps, coverage exclusions, sources, study priorities, retest questions and employer-question suggestions. It does not fabricate project experience or predict a hiring outcome.

## Files

- `SKILL.md`: simulation workflow and routing.
- `references/`: resume mapping, stage planning, question design, scoring, research and recording.
- `scripts/session.py`: initialize, append events, recover state, generate a complete report.
- `tests/test_session.py`: local ledger/recovery/completeness tests, with synthetic data only.
- `examples/`: fictional session demonstrating the workflow.

Run checks:

```sh
python3 -m unittest discover -s tests -v
```

Install this skill folder with your agent's supported skill installer. Do not store interview records in the public skill checkout. The original MIT license and attribution are preserved; upstream: [Bodemingman/mock-interview-prep](https://github.com/Bodemingman/mock-interview-prep).

## Focus and evidence coverage

Today's explicit practice direction overrides JD breadth. Backend practice can use a full-stack JD without allocating UI questions. Specific topics and representative real projects come from the actual resume and role requirements; no technology is universally mandatory. New sessions use schema v2 with scope/exclusions, project anchors, granular topics, protected sampling reserves and evidence depth. Run `check` before the next question. Actual project evidence and hypothetical extensions are tracked separately; a correct basic answer does not establish mechanism/boundary depth.

See [selection-and-depth](references/selection-and-depth.md) and [example plan](examples/backend-plan.json). Older records remain readable and clearly labelled as coarse evidence. The ledger can enforce declared scope and completeness, but cannot prove that a model labelled a question accurately or that its reference answer is technically correct. The automated scenarios validate these safeguards, not a real candidate's interview outcome.
