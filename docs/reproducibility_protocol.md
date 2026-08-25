# Reproducibility Protocol

## Scope

This protocol defines the records required to reproduce a computational
locomotion experiment from the repository. Reproduction means replaying the
declared software workflow and checking the resulting artifacts and metrics.
It does not establish biological validity, clinical prediction, diagnosis, or
drug response.

The protocol is cumulative: every stage must retain its inputs, configuration,
versions, seed policy, output manifest, and checksums.

## Runtime reproducibility

Record the following before a real run:

- repository commit and working-tree state;
- Python 3.12.x;
- FlyGym 2.1.0, MuJoCo 3.9.0, and `flygym_demo` availability;
- NumPy, PyYAML, Matplotlib, and all optional package versions;
- operating system, CPU/GPU model, driver/runtime information, and available
  memory;
- output of `python scripts/check_runtime.py`;
- installation command and dependency lock or package metadata used.

The runtime checker is read-only. A failed runtime check is a stop condition;
do not proceed by substituting another Python or native backend without
recording a new runtime identity.

## Dataset reproducibility

For every imported or generated dataset, retain:

- dataset identifier and category;
- source provenance and acquisition record;
- rollout JSON/NPZ names and format version;
- metadata, timestep, frame count, and duration;
- manifest and SHA-256 checksums;
- the exact configuration and seed used to produce the rollout;
- validation report and any excluded/corrupt files.

Never overwrite an input dataset in place. A repaired or re-exported dataset
gets a new version or output directory and a new manifest.

## Experiment reproducibility

Record the experiment or campaign configuration, proxy values, seed list,
steps, duration, timestep, execution order, retry policy, and output path.
Sequential execution is preferred when exact comparison is required. Resume
and retry events must be recorded rather than silently replacing an earlier
attempt.

Each completed run must be identifiable without relying on directory mtime or
an informal notebook state.

## Artifact reproducibility

For each stage, record producer version, input paths, input hashes, output
paths, output hashes, manifest status, and warnings. JSON reports should retain
the configuration and provenance fields used by the producer. A missing
manifest or checksum is an audit finding, not a harmless cosmetic difference.

The existing provenance utilities provide SHA-256, stable configuration hashes,
git commit, software version, seed, and environment fields. They must be
called with the actual files from the run; do not fill an unknown value from
memory after execution.

## Figure reproducibility

Every figure record must include:

- the source metric/pose/report artifact and its checksum;
- figure-generating module and version;
- plotting configuration, filters, units, and frame/time window;
- output format and resolution;
- whether metadata, fonts, browser rendering, or rasterization can vary.

Figures are reproducible only when their source data and plotting parameters
are preserved. A screenshot without its source artifact is not sufficient.

## Statistical reproducibility

Before analysis, freeze the grouping variable, inclusion/exclusion rules,
calibration/holdout split, estimator, confidence interval method, missing-data
policy, outlier policy, and random seed policy. Record the exact input table
and software versions used for each result.

Do not report a statistical result when the number of independent experimental
units, target definitions, or required assumptions are unavailable. A repeated
seed is not automatically an independent biological replicate.

## Publication reproducibility

The release package should contain or link to:

- source commit and installation instructions;
- runtime report;
- dataset registry and checksums;
- experiment configurations and seeds;
- analysis, validation, and figure manifests;
- tables, captions, supplementary artifacts, and report sources;
- known limitations and scientific boundary statement;
- citation and license metadata.

The paper must distinguish computational simulation results from external
biological evidence. A reproducible software run is not a reproducible wet-lab
experiment.

## Stop conditions

Stop and record the corresponding status when any of the following is missing:

- certified runtime;
- approved dataset or dataset manifest;
- configuration or seed provenance;
- input/output checksum;
- quantitative calibration target;
- required validation split or external evidence.

Use `WAITING_RUNTIME`, `WAITING_DATASET`, or `WAITING_TARGET_DATA` instead of
creating substitute values.
