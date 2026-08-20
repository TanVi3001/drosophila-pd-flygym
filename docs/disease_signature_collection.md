# Disease Signature Collection Workflow

This document defines the internal, human-in-the-loop process for collecting
literature evidence that may be used to construct computational disease
signatures. It does not populate the database, run searches, infer phenotype,
or make biological claims.

## Workflow

```text
Search
  |
  v
Screen
  |
  v
Extract
  |
  v
Review
  |
  v
Approve
  |
  v
Phenotype Atlas
  |
  v
Calibration
```

## Search

Use the approved [search strategy](../research/systematic_review/search_strategy.md)
for PubMed, Europe PMC, Crossref, Google Scholar, Web of Science, and Scopus.
Preserve the exact database-specific query, search date, filters, export, and
operator. Do not treat a search result as evidence until the source record has
been reviewed.

## Screen

Enter one record per candidate in the blank
[screening form](../research/systematic_review/screening_form.csv). Check the
abstract and full text as applicable, record inclusion or exclusion and the
reason, and retain reviewer/date information. A missing field is not a reason
to invent a value; it is a reason to mark the record unclear or pending.

## Extract

Extract only values directly reported by the source. Use the
[extraction form](../research/systematic_review/extraction_form.csv) and retain
gene, genotype, assay, age, sex, temperature, arena, metric, unit, sample size,
variance, figure/table/page, supplement, and notes. A plotted value may not be
transcribed without a documented extraction rule and source reference.

## Review

Complete the [eligibility checklist](../research/systematic_review/eligibility_checklist.md)
and [quality assessment](../research/systematic_review/quality_assessment.md).
Quality fields describe reporting and study context; they do not become an
automatic quality score. Resolve conflicts through a documented second review.

## Approve

Approval requires sufficient provenance, assay definition, unit/context, and a
review decision. Store reviewer, date, comments, and any uncertainty. Pending,
rejected, duplicated, or provenance-incomplete records must not become
calibration targets.

## Phenotype Atlas

Only approved candidates may be exported to the existing Phenotype Atlas. Keep
the link to the paper, figure/table/page, supplement, and assay context. The
Atlas record must distinguish a directly reported value from an unavailable
field.

## Calibration

Calibration targets are created only from approved Atlas records after checking
metric definitions, units, time windows, control context, uncertainty, and
compatibility with simulation outputs. Freeze target provenance and the
calibration/holdout plan before fitting. Calibration concordance is a
computational result and must not be described as biological validation.

## Required outputs from the campaign team

- completed search logs and database exports;
- screened records and exclusion reasons;
- extracted values with source references;
- quality assessments without invented scores;
- approval history and unresolved records;
- a traceable set of calibration-ready targets;
- a PRISMA flow populated only from audited counts.

Until these outputs exist, the appropriate state is planning or pending
evidence collection rather than a completed disease signature database.
