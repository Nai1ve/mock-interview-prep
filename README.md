# mock-interview-prep

A Claude Code [Skill](https://docs.claude.com/en/docs/claude-code/skills) for preparing for a real interview you have scheduled. Given the JD + the version of your resume you submitted, it:

1. Predicts the questions the interviewer is most likely to ask (calibrated by interview format & length).
2. Lays out per-question talking points — STAR structure, story material, key data points, follow-up branches.
3. Flags JD-vs-resume risk points and pre-rehearses the defense.
4. Suggests reverse questions you should ask the interviewer.
5. Provides a **Mock mode**: the skill plays interviewer, scores your live answer on 6 dimensions, lets you re-attempt.

Industry-agnostic. Works for engineering, product, growth, design, finance, biotech, sales, education — wherever JD+resume reasoning applies.

Paired skill: [`docx-resume-tailor`](../docx-resume-tailor) — used at application time, before you get an interview invite.

## Why this exists

Generic interview-prep tools give you the same questions for every role: "tell me about a strength", "describe a conflict". Useful, but the value of prep is **targeting**: which exact questions will *this* specific interviewer at *this* specific company ask, given *this* JD and *this* resume?

Existing tools fall short in three ways:
- **Question banks**: large but undifferentiated; you spend prep time reading questions that will never be asked.
- **JD-aware generators** (e.g. `GPTInterviewer`): get the right ballpark questions but stop there — no risk-point defense, no length calibration per interview format, no scoring loop.
- **Mock interview chatbots**: simulate conversation but rarely give actionable feedback ("vague answer" is not improvement signal).

`mock-interview-prep` adds:
- **Probability tiers** (🔴 high / 🟡 medium / 🟢 rare) calibrated to interview length (HR 30-min ≠ hiring manager 60-min)
- **Risk-point defense** — explicit prep for the JD requirements your resume doesn't fully meet
- **6-dimension scoring** in Mock mode (structure / data anchoring / cliché avoidance / ownership / JD match / length control) so improvements are actionable
- **Pairing with a resume tool**: the skill reads the actual tailored docx you submitted, not just the baseline

## How it works (5-step main flow + Mock mode)

### Main flow

1. Gather context: JD × resume × company → 3-way alignment
2. Predict questions (probability tiers, count tuned to interview format)
3. Per-question talking points (full STAR for 🔴, condensed for 🟡, title-only for 🟢)
4. Proactive add-on topics (moments to seize)
5. Reverse questions for the interviewer

### Mock mode (drill loop)

- Skill picks one 🔴 question, asks in interviewer voice
- You answer (text, with self-reported time)
- Skill scores 6 dimensions × 5 points = 30 total; lists top 3 improvements
- Re-do this question / move to the next / exit

See [`SKILL.md`](./SKILL.md) for the full spec.

## Quick start

### Prerequisites

- Claude Code with skill support, OR use as a standalone reference inside any agentic tooling

### Install as a Claude Code skill

```bash
ln -s "$(pwd)" ~/.claude/skills/mock-interview-prep
```

### Run

```
> I have an interview at Acme Corp tomorrow for a Growth PM role.
> Here's the JD: [paste]
> I submitted the resume at ~/Desktop/resume/tailored/Acme_Corp_Growth_PM.docx
> Help me prep.
```

The skill walks the 5-step flow. To enter Mock mode at any time:

```
> let's drill question 1 / mock interview / I'll answer, you score me
```

## Project layout

```
mock-interview-prep/
├── SKILL.md                          # full skill spec (model reads this)
├── README.md
├── LICENSE
└── references/
    ├── interview-stages.md           # 4 interview stages × mindset & focus
    ├── question-bank.md              # 8 question archetypes (A-H) with framing
    ├── scoring-rubric.md             # 6-dimension Mock scoring detail
    └── company-types.md              # interview style by company archetype
```

## Limitations

- Text-only (no audio / TTS / STT).
- The Mock mode does not simulate free-form interviewer follow-ups — it is one structured question per turn with structured scoring.
- The references files are skeletons. As you use the skill across real interviews, enrich `question-bank.md` and `company-types.md` with what was actually asked.

## License

[MIT](./LICENSE)

## Acknowledgements

- The "JD + resume → targeted questions" framing borrows from the `GPTInterviewer` family of tools, extended with probability tiers + scoring loop.
- The "real experience as a library" truth-preservation principle comes from the companion `docx-resume-tailor` skill.
