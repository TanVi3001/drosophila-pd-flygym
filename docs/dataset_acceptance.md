# Dataset Acceptance Criteria

A dataset is accepted only when the existing read-only validation workflow
confirms that all required artifacts are present, readable, internally
consistent, and generated from an approved real rollout.

## Required Artifacts

Each accepted dataset must contain:

- `rollout.json`
- `rollout.npz` (or the supported legacy `rollout_arrays.npz` input before
  canonical export)
- `viewer_pose.json`
- `manifest.json`
- `metadata.json`
- `metrics/metrics.json` and the expected metrics outputs
- `biomarkers` output from the existing biomarker pipeline
- report and figure outputs required by the existing experiment tooling
- validation status `PASS`

## Validation Rules

The existing validator must pass checks for:

- artifact completeness and readable JSON/NPZ data
- non-empty and consistent frame counts
- finite, valid timestamps and a positive timestep when applicable
- finite, non-zero quaternions
- finite COM values when present
- required metric availability
- manifest hashes and metadata consistency during integrity validation

If any required artifact or check is missing, the dataset is `INVALID` or
`WAITING_DATASET`; it must not enter the Experiment Suite as accepted data.
Missing data is reported, never fabricated.

## Acceptance Command

```bash
python scripts/validate_research_workflow.py \
  --dataset datasets/healthy/Healthy_001 \
  --output results/validation/Healthy_001
```

The report is an integrity/readiness report. A PASS does not establish
biological validity, clinical utility, or Parkinson's disease evidence.
