# Computational Disease Calibration Framework

## Scope

This framework adds a reproducible, control-level calibration layer around the
existing healthy FlyGym controller. It does not add a biological brain model,
neuron weights, clinical thresholds, or a treatment model. The parameters are
explicit computational proxies and must be reported as such.

## Data flow

```text
Healthy CPG controller
        |
        v
DiseaseLayer (vigor, coordination, delay, noise, fatigue, asymmetry)
        |
        v
Existing FlyGym simulation
        |
        v
Existing rollout metrics
        |
        v
Literature observations with provenance
        |
        v
Deterministic grid calibration -> independent holdout evaluation
```

The layer is passed to the existing `Perturbation` protocol. It does not own a
simulation, change MuJoCo, or replace `run_locomotion`.

## Disease Layer

`drosophila_pd.parkinson.DiseaseLayer` exposes:

- `motor_vigor`: multiplicative joint-command factor.
- `coordination`: multiplicative CPG coupling factor.
- `initiation_delay_steps`: zeroes commands during an explicit initial window.
- `motor_noise_std`: seeded action noise in controller-action units.
- `fatigue_rate`: linear time-dependent reduction, clipped at zero.
- `asymmetry`: paired left/right action scaling, only when an explicit index map
  is provided by the caller.

All transformations are finite and seed-controlled. No default left/right map
is guessed. The metadata records the intervention stage, parameters and scope.

## Phenotype observations

`phenotype_database.py` loads JSON records with:

- source and citation;
- model context and assay;
- metric and unit;
- numeric value/range when available;
- direction and weighting.

Qualitative observations are retained for provenance but cannot enter numeric
calibration. The template in
`configs/parkinson/phenotype_database.template.json` intentionally contains no
fabricated numeric values.

## Calibration

`calibrate_grid()` accepts a caller-supplied evaluator and a deterministic
parameter grid. The evaluator may invoke the existing simulation runner. The
calibration package itself only computes weighted normalized errors, retains
missing metrics as explicit statuses, selects the lowest complete loss, and can
score an independent holdout target set.

The framework reports `UNAVAILABLE_NUMERIC_TARGET` until unit-matched numeric
observations are entered with their source provenance. A successful numerical
fit is a computational match to the supplied observations, not validation of a
Parkinson disease mechanism.

## Recommended study protocol

1. Run and archive an unperturbed healthy baseline.
2. Extract target values from a specified assay and model context; record units,
   uncertainty and citation.
3. Declare a parameter grid before running candidate conditions.
4. Run each candidate through the existing FlyGym pipeline with a fresh
   simulation state and fixed seed.
5. Select only from candidates with complete metrics.
6. Evaluate the selected parameters on a holdout observation set or a separate
   replicate set.
7. Report failures, unavailable endpoints and sensitivity to the parameter
   grid alongside the selected candidate.

## Execution bridge

The thin execution bridge is:

```bash
python scripts/run_calibration_conditions.py \
  --conditions configs/parkinson/calibration_conditions.yaml \
  --output results/calibration_conditions
```

It calls the existing CPG runner once for the healthy baseline and once for
each condition. It writes one JSON report per condition and `summary.json`. To
score against a validated numeric target database, add:

```bash
python scripts/run_calibration_conditions.py \
  --conditions configs/parkinson/calibration_conditions.yaml \
  --targets path/to/numeric_phenotype_targets.json \
  --output results/calibration_conditions
```

The repository template contains qualitative observations only, so passing
`configs/parkinson/phenotype_database.template.json` intentionally produces
`UNAVAILABLE_NUMERIC_TARGET` until the researcher supplies unit-matched values
and provenance. The command never invents targets and never runs a treatment
or biological inference step.

## Boundary

The current repository supports simulated locomotion, measurement, comparison
and computational calibration. It does not establish biological validity,
diagnosis, clinical prediction, or therapeutic efficacy.
