# Ledger format

`docs/ledger.jsonl` contains one JSON object per line. No comments or blank lines. An empty file deliberately has no authority and fails the checker. Append events after genuine decisions or observations.

## Common fields

| Field | Meaning |
|---|---|
| `id` | Consecutive `E-0001`, `E-0002`, etc. |
| `at` | UTC ISO timestamp, such as `2026-10-14T18:00:00Z`; nondecreasing |
| `simulation_only` | Optional boolean, default false. True for every event in a fictional ledger; never mix modes |
| `kind` | One of the event kinds below |
| `actor` | Object with `name` and `role`: owner, maintainer, assistant, or reviewer |
| `summary` | Short factual description |
| `details` | Object with kind-specific fields |
| `scope`, `version` | Required for scope proposal, approval, decisions, implementation, candidates, verification, acceptance, publication, release, closeout, and revocation |

Use genuine, attributable owner decisions for real ledgers. An actor label cannot authenticate a human. Do not copy simulated approval references into a real project.

## Event fields and prerequisites

| Kind | Required details | Rule |
|---|---|---|
| `charter_adopted` | `revision`, `charter` file reference, `approval_ref` | First event; owner; one adoption per ledger |
| `scope_proposed` | `included`, `excluded`, `criteria`, `required_checks` | Unique scope ID; nonempty unique check names |
| `scope_approved` | `proposal` event ID, `charter_revision`, `approval_ref` | Owner; exact earlier proposal and adopted charter |
| `decision` | `reason` | Inside approved, non-revoked, open scope; cannot expand scope or grant new authority |
| `implementation_completed` | No additional fields required | Approved scope; summarize actual implemented output |
| `candidate_created` | `candidate`, `artifact` file reference | Implementation recorded; globally unique candidate ID and distinct retained artifact path |
| `verification_recorded` | `candidate`, `check`, `result`, `evidence` file reference | Latest candidate; named required check; PASS, FAIL, BLOCKED, or NOT_TESTED |
| `acceptance_recorded` | `candidate`, `result`, `approval_ref` | Owner; ACCEPTED needs latest PASS for every required check; REJECTED can be recorded without passing checks |
| `publication_authorized` | `candidate`, `destination`, `approval_ref` | Owner; exact accepted and unreleased candidate |
| `release_recorded` | `candidate`, `destination`, `location`, `recovery_evidence` file reference | Exact authorized destination; actual receipt after publication |
| `scope_closed` | `candidate` | Latest candidate accepted; authorized publication, if any, has a release receipt |
| `authorization_revoked` | `approval_ref` | Owner; stops subsequent controlled work for that scope; use a new scope for a later grant |
| `issue_opened` | `issue_id`, `state` | Unique issue ID; state OPEN or DEFERRED; adoption recorded |
| `issue_resolved` | `issue_id`, `evidence` file reference | Earlier unresolved issue with observed evidence |
| `correction` | `corrects` earlier event ID, `explanation` | Preserves history; does not mutate authority or state by itself |

All event kinds require the common fields. Owner-only events require a nonempty `approval_ref`. Other events may use any listed actor role. Scope version must match its proposal.

## File references

```json
{"path":"artifacts/release-c1.zip","sha256":"64 lowercase hexadecimal characters"}
```

The actual digest must match the file. Paths are relative to the project root. Absolute paths, parent traversal, and symlink escapes are rejected. Keep old candidate artifacts at distinct paths so earlier evidence remains verifiable.

Calculate a digest with Python:

```sh
python3 -c "import hashlib,pathlib; print(hashlib.sha256(pathlib.Path('docs/CHARTER.md').read_bytes()).hexdigest())"
```

For large artifacts, use a streaming hashing tool. The validator streams artifact hashes itself.

## Example shape

This is an illustration, not an approval. Replace values with real decisions and hashes, then append as one line:

```json
{
  "id": "E-0001",
  "at": "2026-10-14T18:00:00Z",
  "simulation_only": false,
  "kind": "charter_adopted",
  "actor": {"name": "ACTUAL OWNER", "role": "owner"},
  "summary": "Owner adopts project charter revision 1.0",
  "details": {
    "revision": "1.0",
    "charter": {"path": "docs/CHARTER.md", "sha256": "ACTUAL SHA-256"},
    "approval_ref": "ACTUAL OWNER DECISION REFERENCE"
  }
}
```

For a complete valid ledger, read [the fictional example](../examples/pocket-notes/docs/ledger.jsonl).

## State and corrections

A new verification result invalidates the prior acceptance and publication authorization of that candidate. Reaccept and reauthorize after reassessing the evidence. New candidates cannot inherit evidence or acceptance from earlier candidates.

Scope closeout does not resolve issues. Corrections preserve the earlier event and have no automatic state effect. The checker verifies all historical file references, so do not delete or change evidence after referencing it.

## Starter limits

One charter adoption per ledger, UTF-8 JSONL, ledger size at most 20 MiB. No network fetching, command execution, actor authentication, automated ledger writing, or deployment. An external evidence store needs a separate trusted resolver; URLs are not accepted as local file references.

JSON field names must be unique at every object depth. NaN and Infinity are rejected. A new implementation_completed event clears the active candidate; create a new candidate before verification, acceptance, publication or closeout.
