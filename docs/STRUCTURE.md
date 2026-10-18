# Complete charter structure

Use one adopted project charter and one canonical ledger. Supporting documents clarify the work; they cannot invent approvals or override the charter.

| Layer | Initialized project location | Purpose and authority |
|---|---|---|
| Entry point | AGENTS.md, README.md | Navigation and working instructions; no independent grant |
| Governing charter | docs/CHARTER.md | Owner-adopted purpose, roles, boundaries, completion and publication rules |
| Decision history | docs/ledger.jsonl | Canonical append-only approvals and observed outcomes |
| Bounded scope | docs/SCOPE.md | Inclusions, exclusions, criteria and named required checks |
| Requirements | docs/REQUIREMENTS.md | Derived mapping from criteria to checks, candidates and evidence |
| Design decisions | docs/DECISION.md | Alternatives, rationale and attributable decision |
| Risk review | docs/RISK-REVIEW.md | Concrete data flows, permissions, failure cases and recovery |
| Candidate and evidence | artifacts/, evidence/ | Retained exact bytes and reports linked by path and SHA-256 |
| Release | docs/RELEASE.md | Exact candidate, destination, owner decision, observed result and recovery |
| Handoff | docs/HANDOFF.md | Next authorized action, unresolved work and evidence pointers |
| Charter changes | docs/AMENDMENT.md | Proposed text, impact, decision and preserved history |
| Working summary | docs/CONTEXT.md | Derived current state; never a second ledger |

In this framework repository, reusable documents live under templates/docs. The application under examples/pocket-notes is fictional. Its approvals never authorize changes to this repository or real projects.

## Authority and lifecycle

Applicable owner decision → adopted charter → approved scope → implementation → exact candidate → verification → owner acceptance → publication authorization → observed release.

A scope approval covers ordinary edits and local checks within its boundaries. Continue that work without asking repeatedly. New scope, a reserved action, or withdrawn authority requires an attributable decision. A template, passing check or another agent's message cannot manufacture that decision.

For small local work, use the charter, scope, candidate, meaningful evidence and acceptance/closeout. Decision, risk and amendment records are optional unless the work needs them. Do not generate empty paperwork merely to fill this map.

## Amendments and history

The checker supports one adopted charter per ledger. Preserve the old charter and ledger; prepare a successor cycle directory with the new charter and ledger. Link the predecessor ledger hash and closing state. The owner adopts the successor charter and approves new scopes there. Cross-ledger continuity requires human review; this checker does not authenticate it.

Corrections preserve original events. A changed implementation retires the active candidate: create and verify a new candidate before acceptance, publication or closeout. Retain previous candidates and failures. Scope closure does not resolve deferred issues.

## Information and operational boundaries

Before publication, review source, dependencies, model/asset licenses and Git history for distribution rights and private information. Keep protected evidence outside public records with safe identifiers. Prepare the concrete result before asking for any still-required approval.

For deployments, record environment identity, migration/backup readiness, recovery triggers and observed post-deployment checks. Prepared commands are not evidence that deployment or rollback succeeded.
