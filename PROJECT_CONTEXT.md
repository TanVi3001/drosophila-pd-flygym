# Project Context

## Objective

This repository supports an in-silico research prototype for simulating
Drosophila melanogaster locomotion phenotypes with FlyGym, NeuroMechFly, and
MuJoCo. The long-term research direction is to build a reproducible
unperturbed baseline, introduce controlled motor or controller perturbations,
quantify gait phenotypes, and only then explore Parkinson's-disease-like
perturbation scenarios.

This is a computational simulation project. Simulation output must not be
presented as direct evidence from real Drosophila. Biological validation can be
claimed only when supported by external experimental evidence.

## Software Stack

- Python target: 3.12
- FlyGym target: 2.1.0
- NeuroMechFly as the primary fly model
- MuJoCo target: 3.9.0
- Google Colab for execution and prototyping
- GitHub as the source of truth
- Codex for implementation, debugging, and documentation support

## Current Scientific Checkpoint

Milestone C is complete and frozen. The project now has a reproducible
unperturbed simulation baseline that creates the official FlyGym locomotion fly,
adds position and adhesion actuators through the canonical baseline pipeline,
runs a deterministic flat-ground simulation, and records derived locomotion
metrics.

Milestone C is an unperturbed simulation baseline only. It is not biological
validation, not a Parkinson's disease model, and not evidence from real
Drosophila.

Milestone 8B is complete and frozen. The project crossed the joint
materialization boundary exactly once through a canonical, explicitly named
software gate before moving on to the unperturbed locomotion baseline.

Milestone 8B supersedes the historical Session 02 Blocks 8.14-8.19 notebook
sequence. Those historical cells remain important research records, but their
scientifically relevant anatomy/materialization observations are now represented
by repository code and the frozen JSON evidence report.

Verified Block 8.12 invariants:

- Fly object type: `flygym.compose.fly.neuromechfly.NeuroMechFly`
- `fly.skeleton is None`
- `add_joints()` has not been called
- Body segments: 69
- Anatomical joints: 68
- JointDOFs: 204
- Axis order: `AxisOrder.PITCH_ROLL_YAW`
- Pitch DOFs: 68
- Roll DOFs: 68
- Yaw DOFs: 68
- LF leg JointDOFs: 24
- LM leg JointDOFs: 24
- LH leg JointDOFs: 24
- RF leg JointDOFs: 24
- RM leg JointDOFs: 24
- RH leg JointDOFs: 24
- Non-leg JointDOFs: 60
- MJCF body mapping: 69/69
- Missing parent MJCF bodies for JointDOFs: 0
- Missing child MJCF bodies for JointDOFs: 0
- JointDOF to MJCF joint mapping: 0, expected before materialization
- JointDOF to neutral angle mapping: 0, expected before materialization
- Actuator mappings: 0, expected before materialization
- JointDOF names are unique: 204
- JointDOF name round-trip failures: 0

The empty JointDOF, neutral-angle, and actuator mappings are expected before
joint materialization. They must not be interpreted as errors. These Block 8.12
invariants define the frozen pre-materialization state used by Milestone 8B.

## Block 8.12 Reproduction Status

On August 11, 2026, Block 8.12 was independently reproduced from a fresh
Google Colab runtime using repository code:

```bash
python scripts/audit_block_8_12.py --output results/baseline/block_8_12_audit.json
```

Observed clean-runtime versions were Python 3.12.13, FlyGym 2.1.0, and
MuJoCo 3.9.0. The generated JSON report returned `overall_pass = true`,
`skeleton_before_is_none = true`, `skeleton_after_is_none = true`, MJCF body
mapping total 69, missing parent MJCF bodies 0, and missing child MJCF bodies 0.
The other documented Block 8.12 invariants also passed.

This reproduction validates the repository's non-mutating software/anatomy audit
only. It does not validate a Parkinson's disease model, locomotor biology, or
evidence from real flies.

## Milestone 8B Reproduction Status

On August 11, 2026, Milestone 8B was independently reproduced from a fresh
Google Colab runtime using repository code:

```bash
python scripts/run_joint_materialization_milestone.py --output results/baseline/milestone_8b_materialization.json
```

Observed clean-runtime versions were Python 3.12.13, FlyGym 2.1.0, and
MuJoCo 3.9.0. The generated JSON report returned `overall_pass = true` and all
48 documented checks passed.

Verified Milestone 8B transition:

- Pre-state `fly.skeleton is None`: true
- Pre-state MJCF root joints: 0
- Materialization gate used: true
- `add_joints()` executed only through `materialize_joints_explicit_gate`
- Post-state skeleton is materialized as `flygym.anatomy.Skeleton`
- Post-state MJCF root joints: 204
- JointDOF to MJCF joint mapping: 204
- JointDOF to neutral-angle mapping: 204
- Actuator mappings: 0
- MJCF root actuators: 0
- Second materialization attempt rejected: true

This reproduction validates FlyGym/NeuroMechFly joint materialization and
post-materialization anatomy mappings only. It does not create actuators, run
locomotion, implement controllers, or validate a Parkinson's disease model.

## Milestone C Reproduction Status

On August 11, 2026, Milestone C was independently reproduced from a fresh
Google Colab runtime using repository code:

```bash
python scripts/run_healthy_baseline.py --config configs/experiments/healthy_baseline.yaml --output results/baseline/healthy_baseline.json
```

Observed clean-runtime versions were Python 3.12.13, FlyGym 2.1.0, and
MuJoCo 3.9.0. The generated JSON report returned `overall_pass = true`.

Verified Milestone C unperturbed baseline summary:

- Requested duration: 0.5 s
- Timestep: 0.0001 s
- Simulation steps: 5000
- Position actuators: 42
- Adhesion actuators: 6
- Compiled MuJoCo control dimension (`nu`): 48
- Planar displacement: 6.284186050286936 mm
- Mean planar speed: 12.568372100573873 mm/s
- Heading yaw change: 0.2342730946151257 rad
- Thorax height min/mean/final: 0.7660532202481788 /
  0.946592192150494 / 1.0115140447050612 mm
- Raw observations and derived metrics finite: true

This reproduction validates only the deterministic unperturbed FlyGym
simulation pipeline and derived software metrics. It does not establish
biological realism or disease relevance.

## Materialization Boundary And Current Stop Point

Milestone 8B is the authorized materialization boundary:

- `fly.add_joints(...)` may be called only inside
  `materialize_joints_explicit_gate`.
- Do not assign `fly.skeleton` manually.
- Repository anatomy/materialization audit code must not call `add_joints()`
  from any other code path.

Before the Milestone 8B gate:

- Do not call `fly.add_joints(...)`.
- Do not assign `fly.skeleton`.
- Do not intentionally mutate the MJCF model.
- Do not create actuators, sites, or sensors on the live model.

After the Milestone 8B gate, `fly.skeleton`, MJCF joints, joint mappings, and
neutral-angle mappings are materialized. Actuator mappings and MJCF actuators
remain empty by design for Milestone 8B.

Milestone C is the authorized unperturbed locomotion baseline. It creates the
official FlyGym locomotion fly, position actuators, adhesion actuators,
`FlatGroundWorld`, and `Simulation` through the canonical baseline pipeline.

Milestone D is complete and frozen. The controlled perturbation framework runs
paired baseline-vs-perturbed simulations from fresh FlyGym/MuJoCo state while
holding random seed, duration, timestep, world, spawn, baseline controller,
skeleton, actuator architecture, and metric definitions constant.

Milestone D is a controlled software/simulation perturbation framework only. It
does not define a Parkinson's disease mechanism, validate disease biology, or
map a controller parameter directly to dopamine or any other biological
mechanism.

## Milestone D Reproduction Status

On August 11, 2026, Milestone D was independently reproduced from a fresh
Google Colab runtime using repository code:

```bash
python scripts/run_perturbation_experiment.py --baseline-config configs/experiments/healthy_baseline.yaml --perturbation-config configs/experiments/perturbations/identity.yaml --output results/perturbations/identity.json

python scripts/run_perturbation_experiment.py --baseline-config configs/experiments/healthy_baseline.yaml --perturbation-config configs/experiments/perturbations/action_scale_080.yaml --output results/perturbations/action_scale_080.json
```

Observed clean-runtime versions were Python 3.12.13, FlyGym 2.1.0, and
MuJoCo 3.9.0. Both evidence files report git commit
`f886c204d8ad3a95dcd953418a8f9df51927137f`.

Verified Milestone D identity gate:

- Evidence path: `results/perturbations/identity.json`
- `overall_pass = true`
- `identity_equivalence_pass = true`
- Controlled variables match: true
- Fresh fly/world/simulation per condition: true
- Baseline and identity step counts: 5000 / 5000
- Identity comparison deltas: zero across recorded scalar and adhesion metrics
- Action transformation: identity with transform error 0.0

Verified Milestone D action-scale perturbation:

- Evidence path: `results/perturbations/action_scale_080.json`
- `overall_pass = true`
- Perturbation type: `global_action_scale`
- Scale: 0.8
- Intervention target: controller joint-angle commands
- Action shape: 5000 x 42
- Joint-angle transform error: 0.0
- Adhesion commands preserved: true
- Controlled variables match: true
- Fresh fly/world/simulation per condition: true

Observed action-scale simulation response relative to the paired baseline:

- Planar displacement delta: -0.6714494674507625 mm
- Mean planar speed delta: -1.342898934901525 mm/s
- Heading yaw-change delta: 0.03061053070618347 rad
- Body height minimum delta: 0.3917972226323848 mm
- Body height mean delta: 0.5321613121790706 mm
- Body height range delta: -0.0011024944162713046 mm
- Joint action mean delta: -0.06393024147301052
- Joint action absolute mean delta: -0.20487402724275616
- Adhesion duty-factor deltas: 0.0 for all legs
- Adhesion transition-count deltas: 0 for all legs

The action-scale experiment is a generic software/simulation perturbation. It
is not a Parkinson's disease model and is not biological validation.

## Workflow

GitHub is the source of truth. Google Colab is an execution environment.

Project flow:

1. Codex local work on code, tests, and documentation
2. GitHub version control
3. Google Colab execution
4. FlyGym and MuJoCo simulation runs
5. Logs, metrics, and experiment artifacts
6. GitHub or external artifact storage for reproducible outputs

Codex is a coding agent, not the scientific decision-maker. Scientific
interpretation and stage transitions require explicit project-owner approval.

## Reproducibility Requirements

Every experiment should eventually record:

- Experiment ID
- Git commit
- Python version
- FlyGym version
- MuJoCo version
- Environment details
- Random seed, if applicable
- Duration
- Timestep
- Controller parameters
- Actuator parameters
- Perturbation parameters
- Leg or group affected
- Output metrics
- Output files
- Failure or error logs

Small metadata and metrics files may be version-controlled. Large raw artifacts
should stay out of Git unless explicitly curated.

## Future Stages

The planned high-level stages are:

1. Unperturbed baseline (Milestone C, frozen)
2. Controller interface
3. Controlled perturbations (Milestone D, frozen)
4. Gait metrics
5. PD-like perturbation
6. Healthy vs PD-like comparison
7. Potential rescue experiments

No disease-specific modeling should be introduced until the locomotor simulation
infrastructure is stable and the project owner authorizes that stage.
