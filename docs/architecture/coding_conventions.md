# Coding Conventions

- Target Python 3.12 and use the package layout declared in pyproject.toml.
- Prefer pathlib.Path, structured JSON/YAML parsing, and explicit encoding.
- Keep CLI scripts thin; import reusable behavior from src/drosophila_pd.
- Validate inputs at boundaries and return actionable statuses rather than
  swallowing errors.
- Use deterministic ordering for manifests, file lists, and serialized output.
- Keep scientific assumptions in code and documentation explicit.
- Add tests for public behavior, serialization, failure states, and any
  compatibility path that changes.
- Avoid broad refactors, hidden global state, duplicate algorithms, and
  comments that merely restate code.
- Do not commit generated large/raw artifacts unless the repository policy
  explicitly allows them.

The required baseline is:

    python -m compileall -q src scripts tests
    pytest -q -rs -p no:cacheprovider
    git diff --check
