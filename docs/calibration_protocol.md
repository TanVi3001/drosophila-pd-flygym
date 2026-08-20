# Calibration Protocol

## 1. Prepare literature records

Populate the CSV from traceable sources. Do not create values from the
simulation, interpolate missing observations, or assign disease labels to
computational conditions.

## 2. Validate inputs

```bash
python scripts/validate_calibration.py \
  --literature research/literature/phenotype_database.csv \
  --metrics results/calibration_response_grid/metrics.json
```

Resolve invalid fields before scoring. A valid input report is an integrity
result only; it is not biological validation.

## 3. Score archived candidates

```bash
python scripts/calibrate_model.py \
  --literature research/literature/phenotype_database.csv \
  --metrics results/calibration_response_grid/metrics.json \
  --loss weighted_mse \
  --output results/calibration
```

The engine ranks the supplied candidates. It does not call the simulation and
does not silently generate new candidates.

## 4. Holdout validation

Leave-one-paper-out and leave-one-condition-out helpers are available to a
caller that explicitly supplies a validation callback. They are not run by the
CLI automatically. Use them only after the grouping, train/holdout split, and
metric compatibility have been preregistered.

## 5. Review reports

Each run produces:

- `calibration_report.md`
- `calibration_summary.json`
- `parameter_ranking.csv`
- `objective_breakdown.csv`

The report must retain the source paths, objective configuration, missing
targets, candidate parameters, and scope limitations.
