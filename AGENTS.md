# Charter Ledger starter package

This repository contains generic templates and a fictional example. Example approvals are simulations and do not authorize real actions.

Keep private project documents, owner records, credentials, and runtime data out of this package. Maintain the short README, complete process, ledger-format documentation, checker, and example together. Do not claim a passing checker proves consent, security, or deployment success.

Read `docs/CONTEXT.md` for package development status. Validate with:

```sh
python3 tools/check_ledger.py examples/pocket-notes
python3 -m unittest discover -s tests -v
```
