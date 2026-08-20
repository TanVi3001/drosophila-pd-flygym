# Systematic Review Protocol

This document summarizes the internal protocol for collecting literature
evidence that may later support a Disease Signature Database. It is a planning
document, not a completed systematic review and not a statement of biological
effect.

The detailed working templates are in
[`research/systematic_review/`](../research/systematic_review/), including the
[review protocol](../research/systematic_review/review_protocol.md), [search
strategy](../research/systematic_review/search_strategy.md), [screening
form](../research/systematic_review/screening_form.csv), and [extraction
form](../research/systematic_review/extraction_form.csv).

## Scope

The campaign will identify published Drosophila studies involving
Parkinson-related genes or disease-relevant perturbations and locomotion or
motor-behavior outcomes. Candidate gene concepts include Pink1, Parkin, DJ-1,
alpha-synuclein, and LRRK2. Outcomes may include walking, speed, stride,
climbing, turning, pausing, movement initiation, and related measurements when
the assay definition, unit, context, and provenance are available.

The intended output is a curator-approved evidence set for computational
calibration. It is not a clinical evidence synthesis, a diagnosis model, or a
replacement for biological validation.

## Planned stages

1. Define and version database-specific search strings.
2. Search the approved databases and preserve query/date/export metadata.
3. Deduplicate records without discarding the original source records.
4. Screen title and abstract using the blank screening form.
5. Retrieve and assess full text where permitted.
6. Apply the eligibility checklist and record exclusion reasons.
7. Extract directly reported values and context, with page/figure/table
   provenance.
8. Complete the reporting-quality checklist without automatic scoring.
9. Resolve review disagreements and approve eligible candidates manually.
10. Export only approved records to the existing Phenotype Atlas process.

## Governance

No paper search, download, citation entry, phenotype extraction, or target
population is performed by this repository task. The research team must supply
the source records, follow institutional access and storage rules, and record
reviewer/date information for each decision.

## Stopping rules

Stop the campaign when a source lacks sufficient provenance, when units or
assay definitions cannot be reconciled, when eligibility criteria would need
to change after screening, or when reviewer disagreement is unresolved. Keep
the record pending and document the reason rather than inferring a value.

## Relation to downstream work

Approved evidence may later flow through the existing systems as:

```text
Search
  -> Screen
  -> Extract
  -> Quality review
  -> Manual approval
  -> Phenotype Atlas
  -> Disease Signature
  -> Calibration targets
  -> Calibration
```

Each arrow is conditional on complete provenance and compatibility checks.
Missing or incompatible evidence must remain unavailable.
