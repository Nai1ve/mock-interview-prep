# Fictional session: backend-oriented full-stack role

Resume evidence: R1 claims UI development; R2 claims a 40% API latency reduction. The JD requires backend APIs, database reasoning and basic frontend delivery. The resume does not name the database or caching technology.

This example is a comprehensive session. If the user instead asks for backend practice, exclude standalone UI assessment despite the full-stack JD, and use backend-plan.json as the schema example.

## Opening plan

60 minutes, estimated active interview time; offline gaps/research excluded. Experience alignment 6 min, projects 24 min, foundations 15 min, scenario/debugging 15 min. About 7–10 main questions including follow-up time. Backend/data requirements receive protected coverage despite longer UI descriptions in the resume. All 60 minutes are assessment; the final review is outside this budget.

## Branch excerpt

Q2: Your resume says API latency dropped 40%. What did you change, and how was that measured?

Fictional answer: “I removed a repeated lookup. Average latency went from 100 ms to 60 ms in our test.”

Private record: partial. Measurement method, load and tail latency are unclear. Deepen because those answers affect the strength of the performance claim.

Q2.1: What traffic and measurement window did the test use, and what happened to p95 latency?

Fictional answer: “I don't remember the traffic model; we only collected average latency.”

Private record: gap in performance validation, not proof the code optimization failed. Stop this branch because the boundary is established; do not repeatedly ask for an unavailable number. Move to an untested database requirement. No answer or score is shown mid-interview.

If instead the answer supplied a reproducible workload and tail-latency evidence, continue into the implementation's failure modes when useful. The branch is not capped by how many follow-ups have already occurred.

## Final review excerpt (after the entire interview)

Q2/Q2.1 gap: the improvement claim has an average comparison but not enough evidence to generalize to production load or tail latency.

Complete reference answer for the mechanism and validation question: “The resume figure comes from an average changing from 100 ms to 60 ms, which is a 40% decrease. I removed a repeated lookup, but I would need to verify the exact code path and my ownership details before describing that implementation further. The current evidence does not establish the traffic model or p95 improvement, so I cannot claim that tail latency or production latency improved by the same percentage. To validate the result, I would compare the old and new implementation under the same representative request mix and concurrency, separate warm-up from measurement, repeat the tests, and compare error rate, throughput, median and tail latency as well as the average. I would also check whether the eliminated lookup changes data freshness or error handling. Those are proposed validation steps, not steps I can claim were performed in the original project.”

Study action: design a reproducible API benchmark and explain why average and tail latency may diverge. Retest: how would the conclusion change if average latency fell but p95 rose?

A full saved report must separately address every asked question, including other branches omitted from this short illustrative excerpt, and mark untested requirements. Suggested employer question: “What are the team's main latency and reliability goals, and how are changes validated?” The skill does not invent the employer's answer.
