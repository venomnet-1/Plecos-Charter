# Preparing this package for GitHub

## First publication

1. Review the name, README, MIT license, and attribution.
2. Run the checker and test suite.
3. Review every file and the entire Git history for credentials, private records, personal information, and assets you cannot distribute.
4. Create a separate repository for this framework. Keep private product repositories separate.
5. Push the reviewed package. Publish a 0.1.0 release only after its exact contents and public visibility are explicitly authorized.

These instructions describe the publication workflow; they do not independently grant authority to publish a project.

## Using it in a project

Initialize the templates into a new directory, or copy individual templates into an existing project without overwriting its instructions. Place the charter and ledger under docs. Configure CI to run the checker against the real project root. GitHub CI in this package checks its fictional example only.

Use a pull request or issue comment as an owner decision reference, including the author and URL. An assistant must retrieve and attribute the actual decision; drafting a comment is not evidence of approval.

## Pull requests

Explain the concrete change and evidence. Reference scope and candidate IDs. Required reviewers should check authority, meaningful test coverage, known limitations, and release identity. Passing CI does not establish human approval.

## Public project boundaries

Public ledgers must not contain private customer records or credentials. Protected evidence can be referenced by a non-sensitive identifier with a documented review process. Avoid publishing private history simply because the current files are clean.
