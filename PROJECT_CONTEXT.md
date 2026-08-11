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

Block 8.12 is complete. The project is intentionally paused at a
pre-materialization anatomy audit checkpoint.

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
joint materialization. They must not be interpreted as errors.

## Pre-Materialization Boundary

The current phase audits FlyGym and NeuroMechFly anatomy and mapping behavior
without mutating the live fly model. During this phase:

- Do not call `fly.add_joints(...)`.
- Do not assign `fly.skeleton`.
- Do not intentionally mutate the MJCF model.
- Do not create actuators, sites, or sensors on the live model.

The transition into materialization requires explicit authorization from the
project owner.

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
