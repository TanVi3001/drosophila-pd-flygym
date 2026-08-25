# Scientific Audit Checklist

Use this checklist before treating a computational campaign as ready for
analysis or publication. A checked item means that evidence is attached, not
that the repository has been scored.

## Runtime

- [ ] Python 3.12.x is recorded.
- [ ] FlyGym, MuJoCo, and `flygym_demo` versions are recorded.
- [ ] `python scripts/check_runtime.py` output is archived.
- [ ] OS, CPU/GPU, driver, and native backend information is recorded.
- [ ] The source commit and installation metadata are recorded.

## Dataset

- [ ] Dataset source and identifier are recorded.
- [ ] Manifest and SHA-256 checksums are present.
- [ ] Metadata, frame count, timestep, and duration are consistent.
- [ ] No missing, duplicate, corrupt, NaN, or Inf trajectory artifact remains.
- [ ] Inclusion and exclusion decisions are documented.

## Simulation

- [ ] FlyGym configuration and world/terrain configuration are archived.
- [ ] Simulation steps, duration, timestep, and seed are archived.
- [ ] Recorder and export versions are recorded.
- [ ] The run was executed on the declared runtime.
- [ ] No synthetic or manually fabricated rollout is included.

## Metrics

- [ ] Metric definitions and units are fixed before comparison.
- [ ] Missing or unavailable metrics are reported explicitly.
- [ ] Metric inputs and output hashes are recorded.
- [ ] Frame/time filters and aggregation rules are recorded.

## Calibration

- [ ] Literature mapping was manually reviewed.
- [ ] Quantitative targets have provenance, unit, uncertainty, assay, and
  control context.
- [ ] Calibration and holdout data are separated before fitting.
- [ ] Parameter bounds and loss function are archived.
- [ ] Seed policy and failed attempts are recorded.

## Validation

- [ ] Validation reference data are identified and hashed.
- [ ] The comparison rule and acceptance criteria are preregistered.
- [ ] Outliers, missing data, and failed artifacts are reported.
- [ ] Computational concordance is not described as biological validation.

## Statistics

- [ ] Independent experimental units are defined.
- [ ] Grouping, resampling, confidence interval, and effect-size methods are
  recorded.
- [ ] Statistical assumptions and missing-data policy are documented.
- [ ] The exact input table and software versions are archived.

## Figures and tables

- [ ] Every figure/table has a source artifact and checksum.
- [ ] Captions state units, sample/seed count, and analysis scope.
- [ ] Plotting configuration, filters, and export resolution are recorded.
- [ ] Supplementary assets can be traced back to source artifacts.

## Repository and release

- [ ] Tests, compileall, and diff checks pass in the release environment.
- [ ] README, installation, runtime, citation, and license files agree.
- [ ] Release manifest and archive checksum are present.
- [ ] Known limitations and open research gaps are included.
- [ ] No generated result is included without provenance.

## Final scientific boundary

- [ ] Claims are limited to computational locomotion and the supplied data.
- [ ] The work is not described as a biological Parkinson model, diagnosis,
  clinical prediction, drug discovery result, or therapeutic validation.
