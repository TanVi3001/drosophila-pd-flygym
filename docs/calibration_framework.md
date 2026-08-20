# Literature-Constrained Computational Phenotype Calibration

## Purpose

This layer compares metrics already produced by the repository with explicitly
supplied literature records. Its output is a calibrated **computational
phenotype**, not a biological Parkinson model, a drug model, a neural
simulation, or a clinical prediction.

```text
Literature CSV
     |
     v
Phenotype targets + provenance
     |
Archived simulation metrics
     |
Objective function
     |
Candidate ranking/report
```

The engine never starts FlyGym or MuJoCo. A caller or existing experiment
runner must produce and archive the metrics first.

## Package boundaries

- `phenotype_database.py`: validates the CSV contract and converts populated
  fields to provenance-bearing targets. Blank fields remain unavailable.
- `objective_functions.py`: weighted MSE, weighted MAE, Huber, and cosine
  objectives with normalization and missing-value policies.
- `parameter_space.py`: continuous, discrete, and categorical declarations,
  bounds, defaults, constraints, and deterministic sampling.
- `optimizer.py`: dependency-free grid implementation plus interfaces for
  future random, Bayesian, Optuna, CMA-ES, and SciPy backends.
- `calibration_engine.py`: evaluates supplied candidate metrics only.
- `validation.py`: finite-value checks and statistical/holdout helper
  functions. Holdout callbacks are caller-supplied and are not run implicitly.
- `report.py`: writes the JSON, Markdown, ranking, and objective breakdown
  artifacts.

## CLI

```bash
python scripts/validate_calibration.py \
  --literature research/literature/phenotype_database.csv \
  --metrics path/to/metrics.json

python scripts/calibrate_model.py \
  --literature research/literature/phenotype_database.csv \
  --metrics path/to/metrics.json \
  --output results/calibration
```

`metrics.json` may be a direct metrics mapping, a report containing
`metrics`/`derived_locomotion_metrics`, or a list of candidate records. No
rollout is parsed twice and no simulation is run by either command.

## Scientific boundary

The framework may report how closely supplied computational metrics match
supplied numeric observations under a declared objective. It must not call a
condition a disease stage, claim dopaminergic mechanism, claim treatment
response, replace wet-lab data, or make a clinical statement.
