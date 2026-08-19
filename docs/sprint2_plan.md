# Sprint 2 Plan

Sprint 2 is an execution plan for real FlyGym data. It does not run a
simulation, generate a dataset, or add a scientific model.

## Week 1: Runtime and Smoke Test

- Create or activate the pinned Python 3.12 environment.
- Verify FlyGym 2.1.0, MuJoCo 3.9.0, and `flygym_demo`.
- Run `python scripts/check_runtime.py`.
- Run the existing smoke workflow only after the runtime gate passes.
- Validate the first real rollout and viewer pose before batch execution.

## Week 2: Healthy Datasets

- Generate or import `Healthy_001` through `Healthy_020` with the existing
  resume-safe generator.
- Validate every raw and derived artifact.
- Run the existing analysis, biomarker, and report stages.
- Record manifests, checksums, provenance, and failures.

## Week 3: Reserved Computational Comparison Groups

- Confirm approved configurations and data policy for PD Mild, PD Moderate,
  and PD Severe labels before execution.
- Generate/import only real approved rollouts using the existing pipeline.
- Do not interpret group labels as biological Parkinson's disease stages.
- Validate each group and stop on the first incomplete or inconsistent batch.

## Week 4: Experiment Suite and Final Validation

- Run the existing Experiment Manager over accepted datasets.
- Generate the existing statistics, biomarker, comparison, and report outputs.
- Run research validation and integrity checks.
- Build the paper package only after all upstream gates pass.
- Archive manifests and a reproducibility record.

## Exit Criteria

Sprint 2 is complete only when the runtime, dataset acceptance, Experiment
Suite, biomarker, validation, viewer, and publication checks are supported by
real artifacts. A planned matrix or an empty dataset directory does not meet
an exit criterion.
