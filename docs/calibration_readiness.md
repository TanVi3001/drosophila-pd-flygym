# Calibration Readiness Checklist

Calibration should begin only when every required input is verified and
traceable.

- [ ] Phenotype Atlas complete
- [ ] Disease Signature complete
- [ ] Calibration targets complete
- [ ] Holdout selected
- [ ] Metrics compatible
- [ ] Runtime verified

## Required evidence

- Every target has a paper, assay, unit, source location, and reviewer record.
- Target definitions are compatible with the available simulation metrics.
- Calibration and holdout records are frozen before fitting.
- Seeds, parameter bounds, normalization, loss components, and unavailable
  metrics are recorded.
- The runtime version and dataset provenance are recorded.

An unchecked item means calibration is pending. It must not be replaced by an
assumption or an inferred value.
