# Model-native search and verification

Use the host model's available web search and page-reading tools. A skill does not itself grant browsing capability: discover the provided tools, use them if present, and do not require a separate paid API or pretend a search occurred. Do not build or call an unconfigured external search endpoint.

Before the interview, extract role-relevant technologies and stated versions. Research consequential current changes, deprecations, semantic differences and common misconceptions. Prefer official documentation, release notes, specifications and maintainer explanations. Open the supporting source; a search snippet alone is not verification. Community interview accounts may suggest topics, but cannot establish correctness or “high frequency” without evidence.

Useful queries combine technology/version with an actual mechanism or requirement, for example a runtime's cancellation semantics or a database's isolation documentation. Omit names, contact information, company-private project details and the full resume. Do not paste private answer logs into search.

For each used source persist a source event containing id, query, title, URL, retrieved_at, technology/version (or unknown), claim supported, and whether it was verified from page content. Separate publication date from retrieval date. Explain why a newer topic matters to this role; do not ask release trivia merely because it is new.

During simulation, search narrowly when answer correctness is uncertain or a version boundary matters. Do not reveal the resulting answer to the candidate before the branch closes. Research/bookkeeping does not consume the default active-interview budget. For strict wall-clock mode, the deadline remains in force. Record inaccessible/conflicting evidence and defer judgment if needed.

Before finalizing a reference answer, verify material current/version-sensitive claims and attach source links near the relevant answer. Stable knowledge may be used without claiming it was newly researched. If tools/network fail, mark current verification unavailable, avoid unsupported “latest” claims, and continue on stable questions if appropriate. Ask the user for configuration only if they explicitly require a search provider unavailable in this environment.
