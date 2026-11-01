---
name: mock-interview-prep
description: Run a time-budgeted mock job interview grounded in the candidate's actual resume and job description. Honor the requested practice focus, map resume evidence to specific topics, adapt probing depth, research current topics, and save a complete interview review.
---

# Mock Interview Prep

Run one realistic simulation, not a coaching loop. Use the user's language. Cover the whole role, including nontechnical roles; do not assume a frontend, full-stack, or engineering interview. Do not rewrite the resume or require another skill.

## Establish the session

**Selection priority: today's explicit practice goal → actual resume evidence → relevant JD/level → live answer evidence.** A full-stack JD does not override “today practise backend”. Reuse a stated focus; if absent, ask which direction (backend/frontend/Agent/comprehensive or another role) together with missing essentials. Do not default to comprehensive practice from the JD alone. Show the focus, included/excluded domains and priority projects in the opening plan. Backend practice normally excludes standalone UI/component/JS questions; API consumer boundaries are relevant only when they test the chosen backend skill. Do not later “complete the JD” by adding excluded domains.

Read [selection-and-depth](references/selection-and-depth.md) before planning and before material replans. Create new records with `schema_version: 2`: practice scope, individual projects, granular evidence claims, specific topics, protected sampling time and target depth are required. Never bundle multiple stacks into a single claim/topic such as “Java/Python/SQL/Redis/MySQL”. Old logs remain readable; do not describe their coarse tags as new-schema evidence.

Read the entire available resume and JD before selecting questions. Ask only for missing essentials: resume, JD (or a clearly labelled provisional role profile), interview stage, and duration. Reuse supplied information. If duration is unspecified, propose 45 minutes and let the user adjust it before starting. General practice does not require a scheduled real interview.

Read [resume-mapping](references/resume-mapping.md) and the relevant guidance in [interview-stages](references/interview-stages.md). Build an evidence map of resume claims against JD requirements. Absence from the resume means unverified, not absent ability. Never invent experience, ownership, numbers, employers, or technologies.

Present a compact plan: total minutes, clock method, modules with minutes and percentages summing to 100%, expected main-question ranges, and domain coverage. Allocate all interview time to assessment. There is no timed reverse-question or wrap-up module; the final report and suggested reverse questions are outside assessment time. Plan by time first, then derive question counts from complexity; follow-ups are included in their parent's budget. A deep project and a factual question need different time allowances. Counts are estimates, not promises or stop conditions.

Default to an **active interview budget** in asynchronous text. Explicitly label elapsed minutes as estimates based on expected spoken-answer duration and questioning time; exclude offline waiting, research, bookkeeping, and final report writing. Do not infer speaking speed from message timestamps. If the user requests a strict wall-clock simulation and clock tools exist, record start/deadline, include waiting as disclosed, and check the clock after every answer and before another question. Without reliable clock tools, disclose the limitation and use estimates. Never claim exact timing from text alone.

Read [technical-research](references/technical-research.md). Before the first question use model-native search to inform role-relevant version-sensitive topic selection, or explicitly record that research was unavailable or not needed for stable fundamentals. End-of-interview source lookup is answer verification, not evidence of pre-interview research. Before asking the first interview question, initialize local records using [session-records](references/session-records.md). A new local record is implied by this workflow; do not upload it or commit it. If file tools are unavailable, keep a clearly labelled in-chat ledger and explain persistence/resume limitations.

## Conduct the simulation

Read [question-bank](references/question-bank.md). Ask one question at a time and wait for the full answer. Ground project prompts in specific resume claims. Probe JD requirements independently when resume evidence is weak. Keep the candidate-facing question natural; do not reveal the answer, score, diagnostic checklist, or future questions mid-interview.

After each answer, persist it and assess the specific topic at its demonstrated depth. Before every next question run `session.py check --dir SESSION`, inspect unsampled priority topics, actual project distribution and protected remaining time, then choose:

- **Deepen** when there is a consequential ambiguity, contradiction, unproven claim, or valuable next layer whose answer would change the assessment.
- **Branch** when a dependency, failure case, alternative, or cross-domain connection needs validation.
- **Move on** when evidence is sufficient, the same evidence is repeating, the candidate has clearly reached a knowledge boundary, or another untested requirement has greater value within the remaining budget.

Correctness of a short conclusion establishes at most basic evidence. If the topic targets mechanism/boundary depth, identify what evidence is still missing before moving on. When a candidate answers strongly, probe why/how, counterexamples or failure paths where useful. When a candidate clearly lacks the prerequisite, record the boundary and switch topics; lack of JS knowledge must not reduce Redis/MySQL/concurrency allocation. Do not move on just because another question type has not been used. Do not award mechanism/boundary depth without specific supporting answer evidence.

There is **no fixed follow-up limit**. A clear gap is a reason to record it, not to repeatedly demand the same unknown answer. A strong answer is not automatically permission for endless depth. Follow-ups should test mechanisms, implementation, trade-offs, failures, boundaries, and validation only where relevant. Record why the branch continued or stopped.

Track two coverage axes: question type (project/fundamentals/scenario/behaviour/etc.) and role domain (e.g. backend/data/frontend/security, or the relevant nontechnical domains). Broad question types do not prove broad domain coverage. After each answer, compare actual coverage/time to plan. Question-type changes inside the same business story are not new project coverage. Return to other relevant resume projects rather than continually inventing hypothetical extensions of the easiest project. Reallocate time transparently when valuable depth changes the plan; preserve time for critical untested requirements. Do not silently let the richest resume project consume the whole interview. Show a brief progress update at module transitions or material replans, without scores or hints.

Persist each question, answer, evidence-backed assessment, source and replan before moving on; use the bundled script, not just model memory. Read [scoring-rubric](references/scoring-rubric.md). Do not use STAR or quantification as universal criteria. Do not grade unknown facts as wrong; verify them or mark uncertain. Do not block progress on a score threshold.

## End and deliver

Stop asking questions when the disclosed time budget is exhausted, the user ends the interview, or the planned core coverage is complete and further questions add little evidence. Do not append “three more questions” after reaching the end. If the time limit arrives during an answer, let that answer finish and report any overrun. Uncovered areas remain untested; budget exhaustion does not imply mastery or complete coverage.

Record a finish event with the actual reason. Then produce and save the complete report defined in [session-records](references/session-records.md):

- Planned versus actual coverage/time, with estimated versus measured timing clearly distinguished. Include practice focus/exclusions, real versus hypothetical project coverage, and per-topic target versus observed depth. A question mentioning a technology is not proof of tested mastery.
- Every asked main question **and follow-up**, answer summary, evidence-based critique, missing knowledge, and a complete reference answer. Do not replace answers with “use STAR”, outlines, or three improvement bullets. Group related follow-ups into a coherent answer only if each is explicitly addressed. Separate hypothetical best practice from the candidate's actual experience; mark missing project facts as candidate-supplied details needed.
- Domain-specific strengths and gaps, prioritized study actions, and targeted retest questions. “Untested” and “uncertain” are distinct from failed.
- Verified sources, dates and versions for current/version-sensitive claims. Include any failed verification.
- A few role-specific reverse-question suggestions for a real employer. Do not pretend to answer company-internal questions on the employer's behalf.

Use [scoring-rubric](references/scoring-rubric.md) for type-specific evaluation. Scores describe observed answers, not hiring predictions. If output is lengthy, write the complete local report before giving the user a compact summary and file link; do not silently omit answers.

## Resuming

When continuing a previous session, load its plan and event log first, reconstruct pending questions, remaining budget and domain coverage, and resume without repeating answered questions. Ask which session only if the intended one is ambiguous. A resumed wall-clock interview whose deadline has passed is finished unless the user explicitly grants a new budget; an active-budget interview excludes the offline interval.
