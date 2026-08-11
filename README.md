# drosophila-pd-flygym

Research software scaffold for an in-silico Drosophila melanogaster
locomotion simulation using FlyGym, NeuroMechFly, and MuJoCo.

The project goal is to build a reproducible simulation workflow that can compare
an unperturbed locomotion baseline against future controlled perturbations after
the locomotion infrastructure is stable. This repository is the source of truth
for code, configuration, tests, and documentation. Google Colab is used as an
execution environment, not as the canonical project state.

This is a computational model. Simulation outputs must not be presented as
direct evidence from real Drosophila, and this repository does not currently
claim biological validation of any Parkinson's disease model.

## Current Checkpoint

Milestone C is complete and frozen. The canonical repository implementation now
reproduces the pre-materialization anatomy audit, executes the authorized joint
materialization gate once, validates the post-materialization anatomy state, and
runs an unperturbed deterministic FlyGym locomotion baseline.

Milestone C is an unperturbed simulation baseline. It is not biological
validation, not a Parkinson's disease model, and not evidence from real
Drosophila.

Historical Session 02 Blocks 8.14-8.19 are superseded by canonical Milestone 8B
code and JSON evidence. The notebooks remain historical research records.

The verified Block 8.12 pre-materialization anatomy audit found:

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

The verified Milestone 8B materialization checkpoint found:

- pre-state `fly.skeleton is None`
- pre-state MJCF joints: 0
- materialization gate used
- post-state skeleton is materialized
- post-state MJCF joints: 204
- JointDOF to MJCF joint mapping: 204
- JointDOF to neutral-angle mapping: 204
- actuator mappings: 0
- second materialization attempt rejected

The verified Milestone C unperturbed baseline found:

- Python 3.12.13, FlyGym 2.1.0, and MuJoCo 3.9.0
- duration: 0.5 s
- timestep: 0.0001 s
- steps: 5000
- position actuators: 42
- adhesion actuators: 6
- compiled MuJoCo `nu`: 48
- planar displacement: 6.284186050286936 mm
- mean planar speed: 12.568372100573873 mm/s
- yaw change: 0.2342730946151257 rad
- finite observations and derived metrics

## Repository Layout

- `src/drosophila_pd/anatomy/` - anatomy and FlyGym mapping audit helpers
- `src/drosophila_pd/controllers/` - controller interfaces
- `src/drosophila_pd/perturbations/` - controlled perturbation interfaces
- `src/drosophila_pd/experiments/` - experiment orchestration code
- `src/drosophila_pd/metrics/` - gait and locomotion metrics
- `configs/experiments/` - version-controlled experiment configuration
- `notebooks/session_*/` - session-based Colab research notebooks
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

Fresh Google Colab reproduction has passed using Python 3.12.13,
FlyGym 2.1.0, and MuJoCo 3.9.0. The generated
`results/baseline/block_8_12_audit.json` report returned
`overall_pass = true` with `fly.skeleton` remaining `None` before and after the
audit.

## Reproducing Milestone 8B

Milestone 8B can be reproduced with the joint materialization milestone CLI:

```bash
python scripts/run_joint_materialization_milestone.py --output results/baseline/milestone_8b_materialization.json
```

Fresh Google Colab reproduction has passed using Python 3.12.13,
FlyGym 2.1.0, and MuJoCo 3.9.0. The generated
`results/baseline/milestone_8b_materialization.json` report returned
`overall_pass = true`.

This milestone validates FlyGym/NeuroMechFly joint materialization and
post-materialization anatomy mappings only. It does not create actuators, run
locomotion, implement controllers, or validate a Parkinson's disease model.

## Reproducing Milestone C

Milestone C can be reproduced with the unperturbed baseline CLI:

```bash
python scripts/run_healthy_baseline.py \
  --config configs/experiments/healthy_baseline.yaml \
  --output results/baseline/healthy_baseline.json
```

Fresh Google Colab reproduction has passed using Python 3.12.13,
FlyGym 2.1.0, and MuJoCo 3.9.0. The generated
`results/baseline/healthy_baseline.json` report returned
`overall_pass = true`.

This milestone validates an unperturbed simulation baseline for future software
comparisons only. It does not establish biological realism or disease relevance.

## Running Milestone D

Milestone D runs paired controlled perturbation experiments:

```bash
python scripts/run_perturbation_experiment.py \
  --baseline-config configs/experiments/healthy_baseline.yaml \
  --perturbation-config configs/experiments/perturbations/identity.yaml \
  --output results/perturbations/identity.json
```

```bash
python scripts/run_perturbation_experiment.py \
  --baseline-config configs/experiments/healthy_baseline.yaml \
  --perturbation-config configs/experiments/perturbations/action_scale_080.yaml \
  --output results/perturbations/action_scale_080.json
```

These are controlled simulation perturbation experiments. They are not
Parkinson's disease models and are not biological validation.

Fresh Google Colab reproduction has passed for both Milestone D validation
runs using Python 3.12.13, FlyGym 2.1.0, and MuJoCo 3.9.0. The generated
evidence files are:

- `results/perturbations/identity.json`
- `results/perturbations/action_scale_080.json`

Both reports were generated from git commit
`f886c204d8ad3a95dcd953418a8f9df51927137f`.

The identity run returned `overall_pass = true` and
`identity_equivalence_pass = true`, with zero recorded comparison deltas. The
`action_scale_080` run returned `overall_pass = true`, scaled the 42
joint-angle controller commands by 0.8, preserved adhesion commands, and kept
all controlled variables matched between conditions.

For `action_scale_080`, the observed simulation response relative to the paired
baseline included planar displacement delta -0.6714494674507625 mm, mean planar
speed delta -1.342898934901525 mm/s, yaw-change delta
0.03061053070618347 rad, body-height mean delta 0.5321613121790706 mm, and no
adhesion duty-factor or transition-count deltas. These are simulation results,
not biological interpretation.

## Running Milestone E0/E1

Milestone E0/E1 runs generic parameter-response sweeps before selecting any
disease-like computational phenotype:

```bash
python scripts/run_parameter_sweep.py \
  --baseline-config configs/experiments/healthy_baseline.yaml \
  --sweep-config configs/experiments/sweeps/milestone_e1.yaml \
  --output results/sweeps/milestone_e1.json
```

The configured families are `motor_vigor_proxy` and `coordination_proxy`.
These are phenomenological computational proxies, not direct simulations of
dopamine concentration, dopaminergic neuron loss, or biological validation.

Fresh Google Colab reproduction has passed using Python 3.12.13,
FlyGym 2.1.0, and MuJoCo 3.9.0. The generated evidence file is
`results/sweeps/milestone_e1.json`, produced from git commit
`7cb2ed580b8eabb6a363b27f481564751eeb9e48`.

The report returned `overall_pass = true`: all 10 conditions completed, all
completed conditions passed, and both baseline-equivalent conditions passed.

Key simulation response-surface findings:

- Motor-vigor scaling produced a graded reduction in displacement and speed.
- Joint-action magnitude followed the commanded scaling exactly.
- Body-height response was nonlinear.
- CPG coupling reduction had modest effects at intermediate values.
- Near-zero CPG coupling produced large locomotion loss and large yaw deviation.

No E1 parameter value is currently designated as Parkinson's disease, dopamine
depletion, neuron-loss percentage, disease stage, or biological severity.

## Planned Research Stages

1. Unperturbed baseline
2. Controller interface
3. Controlled perturbations
4. Parameter-response characterization
5. Gait metrics
6. PD-like perturbation
7. Healthy vs PD-like comparison
8. Potential rescue experiments
