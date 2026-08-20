# Literature Workflow

This document describes the human-led process for turning paper evidence into
reviewed computational calibration inputs. It does not add code or create an
automated literature workflow.

```text
Paper
  -> Summary
  -> Extraction
  -> Review
  -> Approval
  -> Phenotype Atlas
  -> Disease Signature
  -> Calibration
```

## Paper

The research team supplies the paper and records its provenance, identifier,
access date, and source location. No paper, DOI, citation, or result is
invented by the repository.

## Summary

Complete `research/curation_workspace/paper_summary_template.md` with the
paper's stated model, genotype, assay, metrics, figures, tables, limitations,
and computational relevance.

## Extraction

Transcribe only directly reported values and context into the extraction
templates. Record units, uncertainty, sample size, source page, figure/table,
and supplement references.

## Review

Use the phenotype extraction checklist and the existing eligibility and quality
templates. Missing or incompatible information remains explicit and blocks
approval.

## Approval

A reviewer records the decision, identity, date, comments, and unresolved
issues. Only approved records with complete provenance may proceed.

## Phenotype Atlas

Approved records can be entered into the existing Atlas process. Preserve the
link to the source paper and the exact assay context. The Atlas must distinguish
reported values from unavailable fields.

## Disease Signature

Compatible approved records may be mapped to existing computational signature
fields. Mapping requires matching metric definitions, units, time windows, and
control context.

## Calibration

Only approved, compatible signature targets may be used by the existing
Calibration Engine. Freeze target provenance and holdout assignments before
fitting. Calibration concordance is not biological validation.
