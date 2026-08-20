# Internal Review Protocol

## Purpose

This protocol defines an internal, human-led evidence collection campaign for
building a Disease Signature Database from published Drosophila studies. It is
not a completed systematic review, clinical evidence review, or biological
conclusion. No search has been run as part of this repository task.

## Review question

Which experimentally reported locomotion, motor-control, and related behavior
measurements in Drosophila disease-model studies are sufficiently described,
provenanced, and assay-compatible to be considered as computational calibration
targets?

## Scope

The planned search covers Drosophila studies involving Parkinson-related genes
or disease-relevant perturbations, including Pink1, Parkin, DJ-1,
alpha-synuclein, and LRRK2. The primary outcomes are locomotion and motor
behavior, such as walking, climbing, turning, pausing, speed, stride, and
related measures when their definitions and units are reported.

The review may record context needed for comparability, including genotype,
age, sex, temperature, arena, assay duration, sample size, control group,
variance reporting, and figure/table/page provenance.

## Eligibility framework

Include a record only when it satisfies the approved study scope and the
relevant inclusion checks in `eligibility_checklist.md`. A paper may be
retained for background without contributing a calibration target; this
distinction must be explicit in the screening record.

Exclude or hold for clarification when the model, assay, outcome definition,
source, or provenance is insufficient for the declared use. Do not recover
missing values by inference from prose, plots, or another paper.

## Review stages

1. Run the approved database searches and preserve the query, date, database,
   and result export.
2. Deduplicate records using a documented rule while retaining source records.
3. Screen title and abstract with the blank screening form.
4. Retrieve and assess full text where permitted by the research team.
5. Apply the eligibility checklist and record exclusion reasons.
6. Extract only directly reported values and context into the extraction form.
7. Complete the quality checklist without converting it into an automatic
   score.
8. Conduct manual review and resolve disagreements before approval.
9. Export only approved records to the existing Phenotype Atlas process.

## Roles and audit trail

Each screening, extraction, edit, and approval action requires a reviewer,
date, and note where relevant. Changes must preserve the prior record or an
approved version history. A paper with unresolved provenance or reviewer
disagreement remains pending.

## Data handling boundaries

This repository task does not search databases, download papers, populate
DOIs, create citations, extract phenotype values, or modify the Phenotype
Atlas. The campaign team is responsible for permissions, storage, citation
management, and institutional review requirements.

## Stopping rules

Pause the campaign if the search strategy changes, if eligibility criteria are
changed after screening begins, if a value lacks a source location, or if assay
definitions cannot be reconciled. Document the decision before resuming.
