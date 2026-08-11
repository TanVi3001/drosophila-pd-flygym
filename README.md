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

Milestone E5 is the latest frozen computational checkpoint. The canonical
repository implementation now reproduces the
pre-materialization anatomy audit, executes the authorized joint materialization
gate once, validates the post-materialization anatomy state, runs an
unperturbed deterministic FlyGym locomotion baseline, characterizes combined
motor-vigor and coordination proxy perturbations, validates the frozen E2
candidate's multi-seed robustness, records qualitative concordance against
selected adult Drosophila walking literature, and freezes the preregistered
Milestone E5 computational reversibility evidence.

Milestone C is an unperturbed simulation baseline. It is not biological
validation, not a Parkinson's disease model, and not evidence from real
Drosophila.

Milestones E2, E3, and E4 are also not biological validation and do not select a
validated Parkinson's-disease-like condition. E4 does not tune the frozen
candidate or calibrate simulation values to biological measurements.
E5 does not tune the frozen candidate, does not run a rescue parameter sweep,
and does not claim pharmacological, dopaminergic, mechanistic, biological, or
Parkinson's disease rescue.

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

## Running Milestone E2

Milestone E2 is FROZEN — COMBINED PHENOTYPE CHARACTERIZATION.

It characterizes a compact explicit set of combined motor-vigor and
coordination proxy conditions:

```bash
python scripts/run_combined_phenotype_sweep.py \
  --baseline-config configs/experiments/healthy_baseline.yaml \
  --sweep-config configs/experiments/sweeps/milestone_e2.yaml \
  --output results/sweeps/milestone_e2_combined.json
```

Fresh Google Colab reproduction has passed using Python 3.12.13,
FlyGym 2.1.0, and MuJoCo 3.9.0. The generated evidence file is
`results/sweeps/milestone_e2_combined.json`, produced from git commit
`433269ed11e0475eb973b62d31f469d66843872f`.

The report returned `overall_pass = true`: all 9 conditions completed, all
completed conditions passed, the control-equivalent condition passed, controlled
variables were preserved, and fresh simulation state per condition was declared.

This run composes CPG coupling-weight scaling with joint-angle action scaling,
records both transformations separately, and reports baseline deltas plus
interaction residuals. It is a phenomenological simulation characterization
only; it does not choose or validate a Parkinson's-disease-like condition.

Key E2 observations:

- Speed and displacement interaction effects were mostly close to additive.
- Directional/yaw effects were more nonlinear across combined conditions.
- Motor scale 0.8 with coupling scale 0.75 is a leading computational candidate
  for further validation, not a final or validated disease model.

## Running Milestone E3

Milestone E3 is FROZEN - MULTI-SEED ROBUSTNESS VALIDATION. It runs paired
baseline-vs-candidate simulations for seeds 0 through 4 at 1.0 s duration:

```bash
python scripts/run_candidate_robustness.py \
  --baseline-config configs/experiments/healthy_baseline.yaml \
  --validation-config configs/experiments/validation/milestone_e3.yaml \
  --output results/validation/milestone_e3_candidate_robustness.json
```

The frozen candidate remains `motor_scale = 0.8` and
`coupling_scale = 0.75`, selected before E3 execution from Milestone E2. E3
does not tune those parameters, implement rescue experiments, or validate a
Parkinson's disease model.

Fresh Google Colab reproduction has passed using Python 3.12.13,
FlyGym 2.1.0, and MuJoCo 3.9.0. The generated evidence file is
`results/validation/milestone_e3_candidate_robustness.json`, produced from git
commit `730ab3acd8e5535b93f320a62c19080feca0448f`.

The report returned `overall_pass = true` and robustness classification
`ROBUST`: all 5 paired seeds completed, controlled variables were preserved,
candidate transformations were validated, required observations and metrics were
finite, and displacement/speed deltas were negative for all 5 seeds.

Key E3 aggregate observations:

- Displacement and speed means changed from 13.751281674590993 to
  12.302040063313584, about -10.54%.
- Planar path length mean changed from 19.31485503067457 to
  17.308442670909542, about -10.39%.
- Trajectory efficiency mean changed from 0.7119806020699851 to
  0.7107636180753024, about -0.16%, with mixed seed-wise deltas.
- Joint action absolute mean changed from 1.0256368082597096 to
  0.820559121832831, about -20.00%.
- Body height mean increased from 0.9465522152698778 mm to
  1.4910686043526398 mm and remains an important confound.
- Absolute yaw-change mean increased from 0.10385794490113649 rad to
  0.21120580249246884 rad; the yaw absolute-change delta was positive in 4 / 5
  seeds.

`ROBUST` means computational/software robustness under these tested seeds only.
It does not mean biological robustness, statistical significance, disease
validation, disease severity, dopamine depletion, or mechanistic validation.

## Running Milestone E4

Milestone E4 is LITERATURE-GROUNDED PHENOTYPE CONCORDANCE. It reads the curated
evidence matrix and frozen E3 evidence without running another FlyGym
simulation:

```bash
python scripts/run_phenotype_concordance.py \
  --output results/validation/milestone_e4_concordance.json
```

The evidence matrix is `docs/scientific/e4_evidence_matrix.yaml`. The generated
report classifies adult walking speed/velocity and covered-distance directions
as `CONCORDANT`, while preserving unsupported endpoints such as angular
velocity, distance per movement, centrophobism, climbing, pause/freezing, and
body-height interpretation as `NOT_COMPARABLE`, `NOT_AVAILABLE`, or
`INSUFFICIENT_EVIDENCE`.

The proposed E4 status is `PARTIAL_PHENOTYPE_CONCORDANCE`: reduced locomotor
output in the frozen E3 candidate is directionally consistent with selected
adult walking literature, but this is not biological validation, not a weighted
PD score, not dopamine depletion, and not mechanistic equivalence.

## Running Milestone E5

Milestone E5 is FROZEN - PREREGISTERED COMPUTATIONAL REVERSIBILITY. It runs a
fixed, preregistered computational reversibility experiment over the frozen
E3/E4 candidate:

```bash
python scripts/run_computational_rescue.py \
  --baseline-config configs/experiments/healthy_baseline.yaml \
  --validation-config configs/experiments/validation/milestone_e5.yaml \
  --output results/validation/milestone_e5_computational_rescue.json
```

The fixed conditions are `control` (`1.0 / 1.0`), `impaired_candidate`
(`0.8 / 0.75`), `motor_partial_rescue` (`0.9 / 0.75`),
`coordination_partial_rescue` (`0.8 / 0.875`),
`combined_partial_rescue` (`0.9 / 0.875`), and
`full_computational_restoration_reference` (`1.0 / 1.0`). The midpoint values
come from `(0.8 + 1.0) / 2 = 0.9` and `(0.75 + 1.0) / 2 = 0.875`.

Primary endpoints are `mean_planar_speed_mm_s` and `planar_path_length_mm`.
E5 reports computational recovery fractions using
`(rescue - impaired) / (control - impaired)` and handles near-zero denominators
explicitly. These are simulation quantities only, not biological recovery
percentages.

The frozen Colab evidence is
`results/validation/milestone_e5_computational_rescue.json`. It reports Python
3.12.13, FlyGym 2.1.0, MuJoCo 3.9.0, git commit
`7cffac001488589d089bc49266aa103e7458f476`, 30 / 30 completed condition runs,
and `overall_pass = true`.

Observed primary endpoint classifications:

- `motor_partial_rescue`: `DIRECTIONALLY_RESCUED`
- `coordination_partial_rescue`: `MIXED`
- `combined_partial_rescue`: `DIRECTIONALLY_RESCUED`
- `full_computational_restoration_reference`: reference only

Motor-axis restoration accounts for most of the primary locomotor recovery
observed in E5. Adding partial coordination restoration produced modest and
endpoint-dependent additional effects: combined partial restoration was slightly
higher than motor-only for mean speed but slightly lower for path length.
Combined partial restoration is therefore not universally superior.

The `full_computational_restoration_reference` condition is a software/control
equivalence check. It is not full rescue, cure, L-DOPA response, dopamine
restoration, or Parkinson's disease rescue.

## Planned Research Stages

1. Unperturbed baseline
2. Controller interface
3. Controlled perturbations
4. Parameter-response characterization
5. Multi-seed robustness validation
6. Literature-grounded phenotype concordance
7. Preregistered computational reversibility
8. Gait metrics
9. PD-like perturbation
10. Healthy vs PD-like comparison
11. Potential biological-rescue interpretation, only after external evidence
   and explicit authorization
