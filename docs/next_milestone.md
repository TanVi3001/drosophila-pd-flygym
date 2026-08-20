# Next Research Milestones

This is a research execution roadmap, not a software feature roadmap. It does
not add modules or authorize implementation changes.

## Milestone 1: Literature completed

### Objective

Complete the paper inventory and human review required for a defensible target
set.

### Exit criteria

- paper registry contains only curator-verified entries;
- curation progress is complete for the declared study scope;
- candidates have reviewer, date, status, and provenance;
- approved records are distinguishable from rejected and pending records;
- calibration targets remain empty where evidence is missing.

### Blockers

Missing papers, incomplete source references, incompatible assays, and missing
units must remain explicit blockers.

## Milestone 2: Calibration completed

### Objective

Evaluate declared computational candidates against approved literature targets.

### Exit criteria

- calibration and holdout membership was frozen before fitting;
- target mappings, units, uncertainty, normalization, and loss are recorded;
- healthy identity and candidate conditions pass artifact checks;
- parameters, seeds, unavailable metrics, and failures are reproducible;
- no computational score is presented as a biological conclusion.

### Blockers

No approved numeric or qualitative target, insufficient metric overlap, invalid
runtime, or non-reproducible output stops this milestone.

## Milestone 3: Validation completed

### Objective

Evaluate generalization, repeatability, sensitivity, and limitations without
changing the frozen calibration procedure.

### Exit criteria

- holdout evaluation is complete or explicitly unavailable;
- repeatability across declared seeds/runs is reported;
- sensitivity and identifiability are documented;
- missing data and failed conditions are included;
- external biological validation status is stated accurately.

### Blockers

Calibration leakage, missing holdout data, incompatible units, or unresolved
artifact integrity failures prevent a complete validation claim.

## Milestone 4: Paper submitted

### Objective

Prepare and submit a manuscript whose claims are supported by traceable
computational artifacts and clearly bounded scientific language.

### Exit criteria

- figures and tables have source manifests and reviewed captions;
- methods specify controller, Disease Layer, signatures, calibration, and
  validation procedures;
- results distinguish computational concordance from external evidence;
- limitations, unavailable data, and negative findings are included;
- code, metadata, provenance, and reproducibility materials are archived;
- target journal and submission format are approved by the research team.

### Blockers

No real dataset, missing provenance, incomplete validation, unsupported claims,
or incomplete artifact archive prevents submission readiness.

## Current state

The repository is at the planning and software-readiness stage for this roadmap.
The next action is research-team curation and runtime/data preparation, not the
addition of another framework layer.
