# Worked example: Pocket Notes

Everything about owner decisions and publication in this example is **fictional**. The local export tests are executable; nobody actually published Pocket Notes.

The change adds a deterministic JSON export that preserves note order, quoted text, line breaks, and literal Unicode. It rejects malformed input. CSV export is proposed separately and deferred.

| Events | What happens |
|---|---|
| E-0001 | Fictional owner adopts the mock charter |
| E-0002–0003 | Scope proposed and approved, including two named checks |
| E-0004 | CSV export deferred; it stays unresolved at closeout |
| E-0005–0007 | Implementation and candidate c1 recorded; Unicode check fails |
| E-0008–0011 | Fix creates distinct candidate c2; behavior and recovery checks pass |
| E-0012 | Fictional owner accepts c2, not c1 |
| E-0013–0014 | Publication of c2 authorized; fictional release receipt recorded |
| E-0015 | Scope closed; deferred issue remains visible |

Run the accepted candidate's actual behavior tests:

```sh
python3 -m unittest discover -s examples/pocket-notes -p test_export.py -v
python3 tools/check_ledger.py examples/pocket-notes
```

Run `python3 examples/pocket-notes/artifacts/pocket-notes-0.2.0-c2.py` to see its tiny export. The checker itself does not execute these commands.

Read `docs/ledger.jsonl` beside the evidence reports. Every candidate and report has a SHA-256 reference. The rejected candidate remains present; it is not rewritten to make history look successful.

Recovery means returning to the previous retained candidate in a disposable local exercise. Candidate c1 has the known Unicode-formatting limitation. This is a demonstration recovery target, not a claim that c1 was previously accepted for production.
