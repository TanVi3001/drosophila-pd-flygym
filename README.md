# drosophila-pd-flygym

Research software scaffold for an in-silico Drosophila melanogaster
locomotion simulation using FlyGym, NeuroMechFly, and MuJoCo.

The project goal is to build a reproducible simulation workflow that can compare
healthy and Parkinson's-disease-like locomotor phenotypes after the locomotion
infrastructure is stable. This repository is the source of truth for code,
configuration, tests, and documentation. Google Colab is used as an execution
environment, not as the canonical project state.

This is a computational model. Simulation outputs must not be presented as
direct evidence from real Drosophila, and this repository does not currently
claim biological validation of any Parkinson's disease model.

## Current Checkpoint

Block 8.12 is complete. The verified pre-materialization anatomy audit found:

- Python target: 3.12
- FlyGym target: 2.1.0
- MuJoCo target: 3.9.0
- Body segments: 69
- Anatomical joints: 68
- JointDOFs: 204
- Axis order: PITCH_ROLL_YAW
- Six leg groups: 24 JointDOFs each
- Non-leg JointDOFs: 60
- MJCF body mapping: 69/69
- JointDOF to MJCF joint mapping: 0, expected before materialization
- JointDOF to neutral angle mapping: 0, expected before materialization
- Actuator mappings: 0, expected before materialization
- `fly.skeleton is None`
- `add_joints()` has not been called

## Repository Layout

- `src/drosophila_pd/anatomy/` - anatomy and FlyGym mapping audit helpers
- `src/drosophila_pd/controllers/` - future controller interfaces
- `src/drosophila_pd/perturbations/` - future controlled perturbation interfaces
- `src/drosophila_pd/experiments/` - future experiment orchestration code
- `src/drosophila_pd/metrics/` - future gait and locomotion metrics
- `configs/experiments/` - version-controlled experiment configuration
- `notebooks/experiments/` - Colab-targeted notebooks
- `scripts/` - command-line utilities
- `tests/` - automated checks
- `results/` - local/generated experiment outputs, kept lightweight by default
- `logs/` - local run logs

## Workflow

1. Develop code, tests, and documentation locally with Codex.
2. Commit and push reviewed source changes to GitHub.
3. Pull the repository into Google Colab for FlyGym/MuJoCo execution.
4. Save reproducibility metadata, metrics, logs, and selected small artifacts.
5. Keep large raw artifacts outside Git unless explicitly curated.

## Reproducing Block 8.12

Block 8.12 can be reproduced with the non-mutating audit CLI:

```bash
python scripts/audit_block_8_12.py --output results/baseline/block_8_12_audit.json
```

The audit checks anatomy and mapping invariants only. It must leave
`fly.skeleton is None` and does not validate a Parkinson's disease model,
locomotor biology, or evidence from real flies.

## Planned Research Stages

1. Healthy baseline
2. Controller interface
3. Controlled perturbations
4. Gait metrics
5. PD-like perturbation
6. Healthy vs PD-like comparison
7. Potential rescue experiments
