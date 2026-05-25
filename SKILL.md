---
name: mock-interview-prep
description: Use AFTER you have a real interview scheduled. Given the JD plus the tailored resume you submitted, predicts the questions the interviewer is most likely to ask, talking points per question, proactive add-on topics to volunteer, and good reverse questions to ask HR. Includes a Mock practice mode where the skill plays interviewer and scores your answer across 6 dimensions. Does NOT run at application time (use docx-resume-tailor then). Triggers when the user says "interview prep", "predict interview questions", "I have an interview tomorrow at X", "scheduled a phone screen with Y", "help me prepare for this interview".
---

# Mock Interview Prep

## When to Use

**Trigger scenarios:**
- User has received an interview invite: "interview tomorrow at Acme", "phone screen scheduled with Initech", "help me prep for this interview"
- User says: "interview prep", "predict interview questions", "mock interview", "let's practice"

**Do NOT trigger in:**
- ❌ Application stage (use `docx-resume-tailor`)
- ❌ Resume drafting (use `docx-resume-tailor`)
- ❌ Cover letter writing (out of scope)

## Core Philosophy

> **Interview prediction is not guessing what's in the interviewer's head. It is reasoning from JD requirements + your resume highlights + the company's business model to figure out: "what is the biggest pain this hiring manager wants someone to solve, and does this candidate fit?"**

Inspired by `GPTInterviewer`-style "JD + resume → targeted questions" generators, but adds:
1. **Probability tiers** (high / medium / low) calibrated against interview format and length, so you don't drown in 30 hypothetical questions for a 30-min HR screen.
2. **Risk-point defense**: explicitly surfacing where the JD outguns your resume, and pre-rehearsing the defense.
3. **Mock mode**: the skill plays interviewer, scores your live answer on 6 dimensions, lets you re-attempt.

## Hard Guardrails

**NEVER:**
- ❌ Hand the user generic interview clichés ("I'm very interested in your company…").
- ❌ Assume experience the candidate doesn't have (same truth-preserving rule as `docx-resume-tailor`).
- ❌ Make the user memorise answers verbatim — give story material + key data points so they can speak in their own voice.

## Inputs

1. **JD (required)**: text/URL/screenshot of the role being interviewed for.
2. **Which resume version was submitted** (recommended): point to the tailored docx you submitted (e.g. `~/Desktop/resume/tailored/Acme_Corp_Growth_PM_20260523.docx`). If not provided, the skill falls back to inferring from the baseline.
3. **Interview format** (optional but strongly recommended):
   - HR screen / Hiring manager / Technical / Senior round / Onsite / Cross-functional
   - Different formats imply different question patterns (see `references/interview-stages.md`).
4. **Company info** (optional): name, level, any known interview style (startup vs enterprise).

## The 5-Step Main Flow

### Step 1: Gather context + 3-way alignment (JD × resume × company)

Output:

```markdown
## Interview Context

- **Company**: [Company Name]
- **Role**: [Role + Level]
- **Format**: [HR screen / Hiring manager / Technical / Final round]
- **Resume used**: [Path to the tailored docx, or "baseline"]
- **Likely interviewer profile**: [HR / Hiring manager / Cross-functional / Senior leader]
- **Core matches** (JD priorities × resume hits): [3-5 lines]
- **Risk points** (JD requires × resume weak): [2-3 lines, prep defense for these]

⏸ Confirm this read is accurate before I continue.
```

### Step 2: Predict questions (probability tiers, count tuned to interview length)

**Count rule** (avoids over-producing — a 30-min HR screen only fits ~5-8 questions):

| Format | Length | High | Medium | Rare | Risk |
|---|---|---|---|---|---|
| HR screen | 30 min | 5 | 0 | 0 | 2 |
| Hiring manager | 45 min | 7 | 4 | 0 | 2 |
| Hiring manager deep | 60 min | 8 | 6 | 2 | 2 |
| Cross-functional / Technical | 30 min | 6 | 3 | 0 | 1 |
| Final / Exec | 30 min | 5 | 3 | 0 | 1 |

Output format:

```markdown
## Predicted Questions

### 🔴 Very high probability (must prep 100%) — N questions
1. [Question] — [What they're really testing / what they want to verify]
…

### 🟡 Medium probability (~70%) — N questions (skip for HR screens)
…

### 🟢 Occasional (~30%) — N questions (deep interviews only)
…

### ⚠️ Risk-point defense questions — likely to be probed
- Example: JD requires "3 yrs SaaS SEO experience", you have 2 → HR may ask "how do you frame this gap?"
```

### Step 3: Per-question talking points (NOT verbatim answers — stories + data + structure)

**Depth rule** (avoids over-long output):
- 🔴 **High probability**: full STAR + key data + traps to avoid + follow-up branches (~200 words/question)
- 🟡 **Medium**: condensed — 1-line direction + key data points (~30 words/question)
- 🟢 **Rare**: title only; expand only if user asks
- ⚠️ **Risk defense**: full expansion (this is where people crash)

🔴 High-probability full format:

```markdown
### Q1: [question]

**What they're really testing**: [the underlying signal HR is verifying]

**STAR framework / your story material**:
- **S (Situation)**: [based on which part of your resume, the context was…]
- **T (Task)**: [the objective at the time was…]
- **A (Action)**: [what you specifically did — lead with data points]
- **R (Result)**: [quantified outcome — pick 2-3 numbers]

**Key data to land**: [3-5 numbers worth dropping]

**Traps to avoid**:
- Do not say [common mistake]
- Do not volunteer [risk you don't need to surface]

**Follow-ups — if they probe**:
- If they ask "why did you do it that way" → [direction]
- If they ask "what would change in a different setting" → [direction]
```

🟡 Medium condensed format:

```markdown
### Q8: [question]
**Direction**: [1 line] | **Key data**: [1-2 numbers]
```

### Step 4: Proactive add-on topics (moments to seize)

```markdown
## Topics to proactively volunteer (timing matters)

1. **When the interviewer asks "anything else to add" / "what's your strength"**:
   - Lead with [your single strongest quantified data point from the resume] + [the capability story behind it].

2. **When asked "why this role"**:
   - Don't say "your company is great" (cliché).
   - Do say: [your real motivation + 1 line on how your capability creates value here].

3. **At a "scoring moment"** — interviewer goes silent / asks you to elaborate:
   - Volunteer [the project you're proudest of] with concrete setting + quantified outcome.

4. **When asked about weaknesses**:
   - Reframe as "growth area" — acknowledge honestly, then show how you actively close the gap.
```

### Step 5: Reverse questions for the interviewer

```markdown
## Reverse questions (signal you're prepared / strategic)

**Don't ask** (signals laziness):
- ❌ "What are the benefits like" / "When will I hear back" / "What are the working hours"

**Do ask** (by stage):

### HR screen
- What's the team's biggest challenge over the next 3-6 months?
- What does "doing well in this role" look like at month 6?
- What's the recent turnover for this role? (politely surfaces "is this a burnout seat")

### Hiring manager / Technical
- What's the current state and the hardest problem in [project mentioned in JD]?
- What's the roadmap for [direction the JD emphasises]?
- Where would my work on [project X from my resume] map onto your team's needs?

### Final / Exec
- What's the company's #1 strategic objective for the next 18 months, and how does this role contribute?
- Growth path / promotion track for this role?
- What's the biggest internal friction or bottleneck right now, and how could I help unblock it?
```

---

## Mode B: Mock practice (drill mode)

**Trigger**: user says "mock interview", "let's practice", "I'll answer, you score me", "drill question N".

**Loop** (one question at a time):

### Step M1: pick a question
- Pick one from Step 2's 🔴 high-probability set (or user-specified).
- Tell the user: which question + interviewer role (HR / Hiring manager / Final) + expected length (1 min self-intro / 5 min project deep-dive / …).

### Step M2: ask in character
- Ask in interviewer voice, not "test prompt" voice.
- Example: «Hi, I'm the HR lead at Acme. Could you give me a 1-minute self-introduction?»

### Step M3: wait for the user's full answer
- ⏸ User types the answer (text only, with self-reported time).

### Step M4: 6-dimension scoring (see `references/scoring-rubric.md`)

Output format:

```markdown
## Score

| Dimension | Your score | Max | Feedback |
|---|---|---|---|
| Structure (STAR) | X/5 | 5 | [specific] |
| Data anchoring (quantified) | X/5 | 5 | [specific] |
| Cliché avoidance | X/5 | 5 | [specific] |
| Ownership clarity | X/5 | 5 | [specific] |
| JD match | X/5 | 5 | [specific] |
| Length control | X/5 | 5 | [specific] |

**Total**: X/30

**Top 3 improvements (priority order)**:
1. [most important]
2. [secondary]
3. [optional]

**Keep doing**:
- [what landed well — re-use next time]
```

### Step M5: loop
- User picks one of:
  - "Re-do this question" — user retries with improvements; rescore; track delta.
  - "Next question" — move to the next 🔴.
  - "Back to main" — exit Mock, return to full prediction mode.

---

## References

- `references/interview-stages.md` — mindset and assessment focus across the 4 interview stages
- `references/question-bank.md` — 8 question archetypes (A-H) with framing notes
- `references/scoring-rubric.md` — 6-dimension Mock scoring detail
- `references/company-types.md` — per-company-archetype (startup / big tech / enterprise / international SaaS) interview style differences

## Connection to docx-resume-tailor

These two skills work as a pair:

```
[Application stage]
JD → docx-resume-tailor → pick template A/B/C → generate tailored docx → submit

[Interview stage]
Interview invite → mock-interview-prep → tell it "I used template X for [Company]" →
it reads the tailored docx + any saved patches
→ outputs predictions + talking points
```

## Out of Scope (deliberately)

- ❌ Voice / TTS / STT mock (text only — no audio simulation)
- ❌ Real-time "interviewer chatbot" mode (this is structured prediction, not free-form chat)
- ❌ Thank-you letters (different skill)
- ❌ Salary negotiation (different skill)

## Status

**MVP scaffold completed 2026-05-22.** This is a skeleton — once you run it through a real interview, iterate based on what was missing:
- Question bank incomplete → fill in
- Industry-specific questions absent → add an `industry-specific.md` reference
- Per-company style not differentiated enough → enrich `company-types.md`

Do not pre-fill specific questions / answers ahead of real use.
