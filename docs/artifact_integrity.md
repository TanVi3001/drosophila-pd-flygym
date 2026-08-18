# Artifact Integrity

`validate_research_workflow.py` performs read-only integrity checks for one
dataset.

## Checks

- SHA256 values declared by `manifest.json` are recomputed from the files.
- Manifest paths must exist and resolve inside the dataset directory.
- `rollout.json`, the NPZ artifact, `metrics/metrics.json`, and
  `viewer_pose.json` are compared for frame-count consistency.
- Metadata and metric documents are parsed as JSON objects.
- Quaternion and COM values are checked for finite, non-zero/valid values.
- Report and figure artifacts are reported as missing when the production
  package is incomplete.

The validator accepts both `rollout.npz` and the legacy
`rollout_arrays.npz` name. It never copies or renames either file.

## Outputs

The command writes `integrity_report.md` and a JSON companion in the selected
validation output directory. A hash mismatch is an integrity failure and must
be repaired at the source/export step; this tool does not repair it.

## Scope

Integrity is provenance and file consistency only. It is not biological
validation, clinical prediction, or a diagnosis.

