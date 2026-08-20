# Developer Handbook

This handbook describes how to work on the existing platform without eroding
its reproducibility boundary.

## Add a module

First identify the existing owner of the behavior. Prefer extending that owner
over creating a parallel manager or registry. Record the source of truth,
inputs, outputs, failure states, and public API impact. Keep imports one-way
along the dependency graph and add the smallest compatibility-preserving
implementation.

## Add a test

Place tests under tests/ next to the behavior they protect. Cover the happy
path, invalid input, serialization, and the relevant unavailable-runtime or
unavailable-dataset state. Do not use synthetic scientific output to make a
research test pass; test fixtures must be clearly computational fixtures and
must not be presented as biological evidence.

## Add an experiment

Use the existing experiment configuration and manager. Declare dataset inputs,
seeds, expected artifacts, validation profile, and provenance. Do not hardcode
rollout data or bypass the existing gates. A missing real dataset must remain a
waiting state.

## Pull requests

1. State scope and protected paths.
2. Explain source-of-truth and dependency impact.
3. Include tests and the exact validation commands.
4. Separate software observations from scientific interpretation.
5. Check manifests, links, generated-artifact policy, and backward
   compatibility.

Use .github/pull_request_template.md and the review checklists under .github/.

## Standards

Target Python 3.12, use pyproject.toml dependencies, prefer standard-library
utilities where practical, use pathlib, and keep scripts thin. Avoid
unrelated formatting churn. See the Architecture Book for the boundaries that
should remain stable.

## Release process

Run the compile, test, and diff checks; inspect protected paths; update the
changelog, citation/version metadata, and release notes together; then follow
.github/release_checklist.md. Release artifacts must identify their source
commit and must not be confused with a new scientific result.
