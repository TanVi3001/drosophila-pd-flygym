# Research Validation Workflow

This repository validates imported FlyGym artifacts without changing them. The
workflow is intentionally separate from simulation, recording, export,
analysis, biomarker, and experiment-management implementations.

## Stages

1. Dataset validation checks the required files, frame counts, timestamps,
   quaternion values, COM values, and availability of computed metrics.
2. Cross-run consistency compares numeric values from multiple completed runs.
   It reports differences only; it does not interpret them biologically.
3. Artifact integrity checks SHA256 entries and consistency between manifest,
   metadata, metrics, report, and viewer-pose artifacts.
4. The end-to-end preflight checks whether the pinned FlyGym runtime is
   available. When it is absent, validation reports `SKIPPED` and starts no
   simulation.
5. The scientific-boundary scan identifies unqualified clinical or biological
   language in Markdown documents for human review.

## Usage

From the repository root:

```powershell
python scripts/validate_research_workflow.py --dataset datasets/healthy/Healthy_001
python scripts/validate_research_workflow.py --compare datasets/healthy/Healthy_001 datasets/pd/PD_001
```

Reports are written to `results/validation/` by default. A missing dataset is
reported as `WAITING_DATASET`; no placeholder rollout, metric, or viewer pose
is generated.

To run the existing simulation demo only after the runtime preflight succeeds,
use `--run-e2e`. This flag is not used by the normal validation test suite.

## Interpretation Boundary

The reports are software and artifact checks. A passing check means that the
observed files satisfy the selected structural checks. It does not establish a
biological result, a clinical prediction, or a medical diagnosis.

