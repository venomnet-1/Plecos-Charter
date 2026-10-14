# Plectos Charter

The Charter Ledger starter framework.

A small framework for keeping AI-assisted software work authorized, traceable, and honest about completion.

**Starter edition 0.1.0 · Python 3.10+ · MIT license**

An AI can implement a change without knowing whether it was authorized, tested, accepted, or published. Charter Ledger keeps those facts separate:

- **Charter:** the rules and who can make decisions.
- **Ledger:** an append-only record of requests, decisions, evidence, and outcomes.
- **Evidence:** files connected to one exact candidate by SHA-256.
- **Context:** a short working summary for the next session; never a second authority.

The useful question is: **Who authorized this change, what was tested, and which exact candidate was accepted?**

## Try it in two minutes

```sh
python3 tools/check_ledger.py examples/pocket-notes
python3 -m unittest discover -s tests -v
```

The first command checks the complete fictional workflow. The second demonstrates that the checker rejects altered artifacts, missing approval, failed verification, stale candidates, and unauthorized publication.

Start a real project in a new directory:

```sh
python3 tools/init_project.py ../my-project
```

Edit `docs/CHARTER.md`, record your owner's adoption in `docs/ledger.jsonl`, and bring the project to your AI assistant with `AGENTS.md`. The new ledger starts empty. Nothing is pre-approved.

## Choose the right amount of process

| Work | Minimum record |
|---|---|
| Reading, discussion, or an unselected idea | No release cycle needed |
| Small approved local change | Scope approval → implementation → candidate → verification → acceptance → closeout |
| A published release or production change | The above, plus exact-candidate publication authorization and release receipt |
| Failed or interrupted work | Record the failure/blocker; leave acceptance and release absent |

A scope approval can authorize a batch of routine edits and local checks. Ask again when scope changes, authority is revoked, or an action was explicitly reserved. Do not make people approve the same thing repeatedly.

## Read the package

- [Complete process](docs/PROCESS.md)
- [Mock charter](templates/docs/CHARTER.md)
- [Ledger format and event rules](docs/LEDGER-FORMAT.md)
- [Complete worked example](examples/pocket-notes/WALKTHROUGH.md)
- [Blank project templates](templates/)
- [GitHub adoption and release checklist](docs/GITHUB.md)
- [AI session prompts](docs/PROMPTS.md)
- [Design tradeoffs](docs/DESIGN.md)

## What the checker does

It validates event shape, chronological order, authority roles, scope references, evidence hashes, candidate identity, and release prerequisites. It reads files; it does not run evidence commands or modify the ledger.

A passing result means **the recorded workflow is internally consistent**. It cannot prove an owner actually gave permission, tests were run honestly, the software is secure, or deployment succeeded. Reviewers must check the evidence and attribution. Filenames, role labels, and hashes are not authentication.

The fictional example is marked `simulation_only: true`. Its approvals never authorize real work.

## Project status

This is a reviewable starter package, not a claim of a unique invention or a production governance standard. Rules files, specification-driven development, decision records, and release gates have existing precedents. This package combines them around a compact decision ledger and exact-candidate evidence.

No private project records are included. The fictional project and all examples were created for this package.
