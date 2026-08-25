# Artifact Provenance

## Provenance chain

Every research result should be traceable through this chain:

```text
Runtime
  -> configuration and seed
  -> FlyGym/MuJoCo rollout
  -> exported dataset and manifest
  -> analysis metrics
  -> biomarkers
  -> calibration
  -> validation/concordance
  -> figures and tables
  -> paper package
  -> release archive
```

Each arrow must preserve input paths, versions, checksums, and status. The
chain describes computational traceability; it does not prove biological
causality.

## Required provenance fields

At minimum, each stage should retain:

- artifact identifier and producer;
- source commit and configuration hash;
- input and output paths;
- input and output SHA-256 checksums;
- schema or producer version;
- random seed and seed role, or `N/A` for deterministic/manual stages;
- Python/package/runtime information;
- timestamps and status;
- warnings, exclusions, and failure/retry history;
- scientific scope statement.

## Artifact classes

### Datasets

Record source, dataset category, rollout format, frame count, timestep,
metadata, manifest, checksums, runtime, configuration, and seed. A dataset
without a manifest or checksum is not provenance-complete.

### Metrics

Record the exact rollout input, analysis version, metric definitions, channel
availability, missing-data decisions, and output checksum. Do not overwrite a
metrics report after changing the input rollout.

### Analysis

Record analysis configuration, selected dataset IDs, frame/time filters, code
version, and generated tables/figures. Preserve unavailable metrics as
`unavailable`; do not infer them from a differently defined endpoint.

### Calibration

Record approved literature target provenance, units, uncertainty, target
selection, loss function, parameter bounds, seed policy, candidate outputs,
and holdout separation. A technical sweep without approved target data is not
a calibration result.

### Validation

Record reference data, comparison rule, dataset split, metrics, warnings,
outliers, missing values, and report version. Concordance is computational
agreement, not biological validation.

### Figures

Record source artifact hashes, plotting module/version, filters, units,
caption, resolution, and export format. Keep the source table or metric file
beside the figure manifest.

### Paper

Record the exact reports, tables, figures, citations, supplementary files, and
manuscript commit used to build the paper package. A hand-edited caption or
table must retain its source and reviewer history.

### Release

Record release version, source commit, archive checksum, dependency/runtime
matrix, included artifact manifest, license, citation metadata, and known
limitations. A release archive should be buildable from the recorded inputs.

## Provenance failure handling

Use an explicit failure or waiting status for missing provenance. Do not repair
history by guessing a seed, replacing a checksum, or copying metadata from a
different run. Keep the original artifact and create a new audited attempt.
