# Literature-driven Calibration Study: Publication Plan

## Status

Planning only. No journal, paper, citation, result, figure, table, or claim is
selected by this document.

## Target journals

Target journal selection is **TBD by the research team** after the study scope,
data availability, and manuscript format are finalized. The final decision
must consider scope, computational-methods policy, data/code requirements,
article type, and reproducibility expectations. No journal name is populated in
this template.

## Required figures

The planned figure inventory is maintained in [`figure_plan.md`](figure_plan.md):

1. System overview.
2. Disease Layer design.
3. Calibration response and parameter selection.
4. Signature matching.
5. Holdout and validation.
6. Discussion of scope and limitations.

Each figure must identify source artifacts, analysis code, caption, units,
uncertainty, and whether it is computational or externally validated. No figure
should be generated until its source data and inclusion criteria are frozen.

## Required tables

The planned table inventory is maintained in [`table_plan.md`](table_plan.md):

1. Literature summary.
2. Calibration targets.
3. Validation results.
4. Ablation and sensitivity analysis.

Tables must preserve paper-level provenance, units, missingness, sample or
experiment structure, and the distinction between calibration and holdout
records.

## Required experiments

- Healthy controller identity and repeatability.
- Single-proxy perturbation response.
- Declared multi-proxy interaction conditions.
- Calibration-set evaluation.
- Frozen holdout evaluation.
- Seed and duration sensitivity.
- Missing-target and unavailable-metric audit.
- Ablation of proxy families and normalization choices.

The exact conditions and parameter ranges must be preregistered before
calibration results are interpreted.

## Required statistics

The statistical method remains TBD until the real literature and simulation
data structure is known. The final protocol must define:

- unit of analysis and dependence structure;
- summary and uncertainty measures;
- repeated-seed aggregation;
- calibration versus holdout comparisons;
- sensitivity to missing values and outliers;
- multiple-comparison handling where relevant;
- reproducibility and reporting of unavailable results.

No threshold or effect size is invented here.

## Expected limitations

- Literature assays may not be directly comparable.
- Metric units and operational definitions may differ.
- Computational signatures are constrained by the healthy controller and
  simulation action space.
- Multiple proxy vectors may produce similar summary signatures.
- External biological validation may be unavailable.
- Calibration concordance must not be presented as biological equivalence.

## Publication gate

Before submission, the team must verify that all claims are supported by
recorded artifacts, every external source has provenance, calibration and
holdout data are separated, and limitations are stated in the manuscript.
