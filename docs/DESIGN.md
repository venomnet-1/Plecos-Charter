# Design and limits

The charter establishes authority; the ledger preserves decisions; immutable candidates prevent evidence from drifting onto different bytes. Context is deliberately subordinate.

JSON Lines is readable, diffable, and supported by the Python standard library. Git supplies version history. A ledger is append-only by policy; this starter does not cryptographically prevent editing, authenticate actors, or provide database transactions.

Owner attribution must be reviewed by humans or a trusted integration. A string such as `role: owner` is not identity verification. Evidence hashes detect changed files, not dishonest reports. SHA-256 links artifacts but does not sign approval.

The checker reads local files and rejects absolute paths, parent traversal, and symlink escapes. It never executes recorded commands. Use CI with read-only credentials and no deployment secrets for checking untrusted pull requests.

There is no AI vendor dependency. An assistant can consume the Markdown instructions; a maintainer can use the workflow without AI.

This starter has one adopted charter per ledger and no automated public release/deployment. Amendments use a linked successor ledger. Scope changes use a new approved scope; changing code creates a new candidate. This avoids treating an edited description as fresh authority.

Larger teams may need authenticated approvals, signed releases, protected branches, retention controls, artifact storage, and separate environments. Add those when the project requires them. Do not claim this starter implements them.
