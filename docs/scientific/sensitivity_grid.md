# Computational Sensitivity Grid

The canonical grid at `configs/parkinson/sensitivity_grid.yaml` contains ten
generic computational conditions: four motor-vigor values, three coordination
values, and three initiation-delay values. It is intended to characterize the
response surface of the existing control pipeline before any literature
calibration is attempted.

Run it with:

```bash
python scripts/run_calibration_conditions.py \
  --conditions configs/parkinson/sensitivity_grid.yaml \
  --output results/calibration_response_grid
```

The runner executes the existing FlyGym locomotion path. It does not create a
new simulation engine, assign disease stages, or interpret the output as
biological or clinical evidence. The generated metrics are computational
responses only.

The grid should be evaluated with finite-value checks, controlled-variable
checks, and response summaries. A non-monotonic response is an observation to
review, not a reason to alter the result. Numeric targets may be supplied later
only when they have traceable provenance, matching units, and compatible assay
context.
