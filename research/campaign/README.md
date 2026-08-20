# Literature-driven Calibration Campaign

This directory contains empty planning templates for a future
literature-driven calibration study. It does not contain papers, citations,
phenotype values, calibration values, or study conclusions.

## Files

- `paper_registry.csv`: curator-owned paper inventory template.
- `paper_registry.schema.json`: JSON Schema for a registry row.
- `curation_progress.csv`: tracking template for review progress.
- `calibration_targets.csv`: empty target-value template.
- `validation_plan.md`: calibration, holdout, statistical, acceptance, and
  failure planning.

## Intended workflow

```text
Paper registry
    -> Human curation
    -> Literature Assistant candidate review
    -> Approved Phenotype Atlas records
    -> Computational signatures
    -> Calibration targets
    -> Calibration
    -> Holdout validation
    -> Publication artifacts
```

The workflow does not download or crawl papers automatically. Curators must
enter and verify source metadata. Only approved, provenance-complete records
may be used as calibration targets.

## Empty-template policy

All CSV files intentionally contain headers only. Do not populate them with
example papers or invented values. Keep source identifiers, assay context,
units, uncertainty, reviewer decisions, and exclusions auditable when real
research curation begins.
