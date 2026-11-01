# Question design

Generate questions against current resume/JD evidence. This is a design framework, not a prediction of a particular employer's actual questions. Do not attach invented probability percentages or “recently asked” labels.

| Type | What to test | Useful follow-up directions |
|---|---|---|
| Experience/alignment | Relevant scope, motivation, actual responsibility | Concrete example; personal versus team ownership; relevance to role |
| Resume project | A named decision, implementation or outcome | Mechanism; alternatives rejected; failure handling; measurement; retrospective |
| Foundations / 八股 | Role-relevant knowledge beyond memorized definitions | Why it works; worked example; counterexample; applicability; version boundary |
| Scenario/design | Decomposition under actual constraints | Clarify load/users/resources; trade-offs; consistency/security; evolution; verification |
| Debugging | Evidence-driven diagnosis | Hypothesis; observation; isolation; fix; regression prevention |
| Coding/algorithm | Ability to implement relevant logic | Correctness; edge cases; complexity; tests; maintainability |
| Behaviour/judgment | Decisions and collaboration in a concrete situation | Conflicting goals; own action; consequences; reflection |

For technical interviews, explicitly allocate fundamentals rather than hoping they appear inside project discussion. Use only relevant stacks: browser/runtime/framework internals for frontend; language/runtime, concurrency, APIs and persistence for backend; networking, OS, data, security, testing or delivery where justified. Do not force every engineering category into every role or assume a technology absent from the inputs.

Stable foundations and newer topics are complementary. A version-release trivia quiz cannot replace mechanism knowledge. Research current topics with technical-research.md and tie them to a JD requirement or resume claim.

Example: resume says “reduced API latency by 40%”. Ask what endpoint/path changed, baseline and percentile, load and measurement method, candidate responsibility, and implementation. Deepen where the answer exposes uncertainty; don't assume cache, SQL or framework choices until supported. A follow-up about database isolation belongs only if the actual system or JD makes it relevant.

Keep an internal dependency tree: a question depending on an unsettled fact waits for that answer. Do not ask a fixed chain regardless of what the candidate says. Record question IDs and parent IDs so the final report can cover every asked branch.
