# Literature-driven Calibration Study: Validation Plan

## Status

This is a planning document. No paper, phenotype, target value, threshold, or
calibration result is populated in this repository by this template.

## Calibration dataset

The calibration dataset will contain only curator-approved literature targets
whose provenance, assay definition, unit, and uncertainty are recorded in
`calibration_targets.csv`. Each target must be traceable to a paper in
`paper_registry.csv` and, where applicable, to the approved Phenotype Atlas
record and signature field.

The calibration set must define before execution:

- inclusion and exclusion criteria;
- metric definitions and units;
- assay and observation-window compatibility;
- target uncertainty representation;
- paper-level grouping rules;
- normalization and weighting rules;
- treatment of unavailable or incompatible targets.

No missing value may be replaced by a fabricated value. A target that cannot be
mapped defensibly is marked unavailable and excluded with a reason.

## Holdout dataset

The holdout set must be separated at the paper or experiment level before
calibration. It must not be used to select parameters, normalization
statistics, weights, or proxy combinations.

The holdout protocol must record:

- the immutable list of held-out papers or targets;
- the signature fields evaluated;
- the normalization reference set;
- the distance/loss method;
- missing-data handling;
- all failed or unavailable comparisons.

## Validation protocol

1. Validate registry and provenance completeness.
2. Validate that every target has a declared unit and assay context.
3. Validate the healthy identity condition before perturbation conditions.
4. Validate parameter bounds and action-contract integrity.
5. Run calibration only on the declared calibration set.
6. Evaluate the frozen holdout set without changing parameters.
7. Repeat stochastic conditions using predeclared seeds.
8. Report sensitivity, identifiability, unavailable metrics, and failures.
9. Preserve manifests and source references for every generated result.

## Statistical protocol

The statistical protocol remains to be selected after the real target structure
is known. It must specify:

- the unit of analysis;
- paper-level or experiment-level dependence;
- repeated-seed handling;
- effect and uncertainty summaries;
- multiple-comparison handling, if applicable;
- sensitivity to missing data and outliers;
- calibration versus holdout reporting;
- reproducibility and random-seed controls.

No statistical method or significance threshold is prefilled here because the
appropriate choice depends on the final dataset and study design.

## Acceptance criteria

A calibration study can be accepted for publication review only when:

- all included targets have curator-approved provenance;
- calibration and holdout membership is frozen before evaluation;
- source units and assay definitions are compatible or explicitly excluded;
- all signatures and distance settings are reproducible;
- missing values and failures are reported;
- results are stable under the declared repeatability protocol;
- computational concordance is clearly separated from biological claims.

The numerical acceptance thresholds are intentionally left for the study
protocol and domain review; this template does not invent them.

## Failure criteria

The study must be marked failed, incomplete, or not interpretable when:

- provenance cannot be established;
- target units or assay definitions are missing;
- calibration data leaks into holdout evaluation;
- output artifacts are inconsistent or non-reproducible;
- required metrics are unavailable without imputation;
- a proxy is presented as a biological mechanism without evidence;
- the runtime or simulation artifact is invalid.

Failure is a reportable outcome. It must not be hidden by deleting rows or
replacing unavailable values.
