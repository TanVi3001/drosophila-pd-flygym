# Research Execution Guide

This guide describes how a research team should use the existing platform for a
literature-driven calibration study. It does not introduce code or a new
workflow implementation.

## 1. Intake paper metadata

Enter curator-verified metadata in the existing campaign templates:

- `research/campaign/paper_registry.csv`;
- `research/campaign/curation_progress.csv`.

Do not invent a DOI, PMID, title, assay, genotype, or citation. Keep the local
paper file and its provenance outside generated results according to the
research team's data policy.

## 2. Review literature candidates

Use the existing Literature Assistant only on local files supplied by the
research team. Its parser accepts explicit structured fields; it does not crawl
or download papers and does not infer phenotype from prose.

For every candidate:

1. inspect the source page and figure/table reference;
2. check assay, units, age, sex, genotype, and sample context;
3. add a curator comment;
4. approve, reject, or edit the candidate;
5. retain the reviewer and review date.

An edit returns a candidate to pending review. A rejected or pending candidate
must not be used as a calibration target.

## 3. Approve Atlas records

Only approved candidates with complete provenance may be exported to the
existing Digital Phenotype Atlas. Preserve paper, figure, table, supplement,
and page references. Missing information remains unavailable and is recorded as
such; it is not filled by inference.

## 4. Build computational signatures

Construct a signature from existing summary artifacts such as `metrics.json`,
`biomarkers.json`, or `rollout_summary.json`. Confirm that metric definitions,
units, time windows, and coordinate conventions are compatible before comparing
literature and simulation signatures.

The signature stage does not read rollout frames again or recompute upstream
analysis. A missing metric remains `unavailable`.

## 5. Define calibration targets

Populate `research/campaign/calibration_targets.csv` only from approved Atlas
records. Each target must include:

- metric name and exact definition;
- literature value and unit;
- source paper and figure/table/page pointer;
- assay context;
- uncertainty or an explicit unavailable status;
- calibration status.

Freeze the calibration set, holdout set, normalization reference, and loss
method before calibration begins.

## 6. Run calibration

Run the existing calibration framework over declared computational candidates.
Record parameter manifests, seeds, input targets, unavailable metrics, loss
components, and output artifacts. Calibration measures concordance with the
declared targets; it does not establish a biological mechanism.

The healthy identity condition must be checked first. Candidate parameters must
remain within the declared parameter space and must not silently change meaning
between calibration and holdout evaluation.

## 7. Validate

Use the existing validation plan to check:

- artifact and manifest integrity;
- reproducibility under declared seeds;
- calibration/holdout separation;
- sensitivity and identifiability;
- missing data and failure handling;
- consistency of units and assay definitions.

Report negative, partial, and unavailable results. Do not delete failed runs or
replace unavailable values.

## 8. Prepare publication artifacts

Use the existing figure, table, and publication plans to assemble only outputs
whose source artifacts are traceable. Captions must identify the computational
scope, units, uncertainty, and limitations. The manuscript must distinguish
simulation concordance from external biological evidence.

## Execution gate

The team should stop and resolve the blocker when runtime, dataset integrity,
provenance, calibration targets, or validation prerequisites are missing. A
`WAITING_RUNTIME`, `WAITING_DATASET`, or unavailable target is a valid research
status, not a result.
