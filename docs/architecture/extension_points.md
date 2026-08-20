# Extension Points

The supported extension points are deliberately narrow:

- Add a new analysis metric in the existing analysis package, with a focused
  unit test and an explicit input/output contract.
- Add an experiment through existing configuration/templates and the
  experiment manager; do not hardcode a dataset list in a script.
- Add a report or export format at the artifact boundary, preserving manifest
  and provenance fields.
- Add a viewer presentation feature in web/ without changing the rollout
  schema or scientific artifacts.
- Add a validation rule as a separate check with an actionable status and
  regression coverage.

Before extending a boundary, document the source of truth, failure state,
serialization impact, and backward-compatibility story. New scientific
interpretations require evidence and review; they are not implied by adding a
metric or display.
