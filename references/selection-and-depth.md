# Selecting the next question

## Scope is chosen for this session

User intent selects the exercise, not the resume's longest paragraph or all responsibilities in a JD. Backend-only, frontend-only, Agent-only and comprehensive sessions are equally valid. A specific topic drill can intentionally use one project; do not impose multi-project breadth against that request. Mixed sessions can allocate a small explicit budget to a secondary domain. Exclude irrelevant topics rather than presenting them as skill gaps in the report.

Translate the focus to a session contract: objective, included domains, excluded domains, relevant projects, concrete topics, and protected minimum **sampling** time for critical topics. A priority topic is required only because this session's user request/resume/JD supports it. Redis, MySQL, concurrency are examples, never universal compulsory modules. If a scope change is requested during the interview, record the user's request in a replan; do not infer permission from a weak answer.

## Map actual material, then choose time and questions

Read the actual resume, not only a prior summary. If the original is unavailable, label the source and limitation. Split a skills list into separate claims only where relevant. Do not treat a technology name as evidence of production usage. Preserve project anchors and personal ownership. Mark hypothetical transfer questions separately from actual implementation questions.

Example for a backend practice session with a financial data scheduler and an Agent service:

- Scheduler: task uniqueness, checkpoint consistency, multi-instance coordination and recovery, based on actual claimed responsibilities.
- Redis: ask whether/how the candidate used it before assuming a lock implementation; examine ownership, expiration and safe recovery if relevant.
- MySQL: actual query/index decision, plan evidence or transaction behavior; do not call one SQL syntax answer “database covered”.
- Concurrency: a real shared-state/failure window, then language or multi-process mechanisms as appropriate.
- Agent service: execution state/versioning or cancellation only if relevant to this session; do not drift into chat UI design.

The topic choices and time distribution change if the user wants frontend, Agent architecture, HR or a narrow specialist drill. Do not hardcode today's personal resume in the reusable skill.

## Evidence depth

| Depth | Evidence needed |
|---|---|
| touched | Term mentioned or question posed; no sufficient independent explanation |
| basic | Correct conclusion/concept and a relevant example |
| mechanism | Causal explanation, concrete implementation or execution sequence |
| boundary | Reasoning through failure/interleaving/counterexample/trade-off and a way to validate |

Target depth follows role seniority, topic importance and available time. A strong answer may already establish multiple layers; do not repeat questions for ceremony. A gap is not evidence of shallowness of the interview if the interviewer actually tested the relevant layer and found a boundary. Record “not investigated” separately from “investigated and missing”.

Each assessment specifies observed depth, evidence supporting that depth, remaining unknowns and why to continue/stop. A high score in basic recall cannot substitute for a missing mechanism probe.

## Scheduling

Before the next question inspect the script's `check` output. Compare two candidates internally: continue the current branch versus sample the most important untested topic/project. State the internal selection reason in the question record. Preserve protected sampling time for unasked priorities. Once sampled, actual depth still needs assessment; sampling is not mastery. If no time remains for further depth, leave it explicitly unverified.

Avoid an entire interview spent in one story by counting **actual project evidence**, not question types or broad tags. If another important project remains untouched, the benefit of another hypothetical UI/interface scenario is usually lower than a genuine implementation question there. When intentionally staying on one project, record why it advances the user's chosen goal.

The script enforces declared IDs, exclusions and sampling reserves, and reports missing depth/concentration. It cannot judge whether a question truly tests its declared topic; review that meaning before asking. Do not mislabel frontend state questions as backend to bypass checks. Weak answers in a secondary domain do not justify spending the primary domain's budget on easier follow-ups.
