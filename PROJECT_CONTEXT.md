# Project Context

## Objective

This repository supports an in-silico research prototype for simulating
Drosophila melanogaster locomotion phenotypes with FlyGym, NeuroMechFly, and
MuJoCo. The long-term research direction is to build a reproducible healthy
baseline, introduce controlled motor or controller perturbations, quantify gait
phenotypes, and only then explore Parkinson's-disease-like perturbation
scenarios.

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

Milestone 8B is complete and frozen. The project has crossed the joint
materialization boundary exactly once through a canonical, explicitly named
software gate and is now paused before healthy locomotion baseline work.

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

## Materialization Boundary And Current Stop Point

Milestone 8B is the authorized materialization boundary:

- `fly.add_joints(...)` may be called only inside
  `materialize_joints_explicit_gate`.
- Do not assign `fly.skeleton` manually.
- Do not call `add_joints()` from any other repository code path.
- Do not create actuators, run locomotion, or implement Milestone C until the
  project owner authorizes that stage.

Before the Milestone 8B gate:

- Do not call `fly.add_joints(...)`.
- Do not assign `fly.skeleton`.
- Do not intentionally mutate the MJCF model.
- Do not create actuators, sites, or sensors on the live model.

After the Milestone 8B gate, `fly.skeleton`, MJCF joints, joint mappings, and
neutral-angle mappings are materialized. Actuator mappings and MJCF actuators
remain empty by design.

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

1. Healthy baseline
2. Controller interface
3. Controlled perturbations
4. Gait metrics
5. PD-like perturbation
6. Healthy vs PD-like comparison
7. Potential rescue experiments

No disease-specific modeling should be introduced until the locomotor simulation
infrastructure is stable and the project owner authorizes that stage.
