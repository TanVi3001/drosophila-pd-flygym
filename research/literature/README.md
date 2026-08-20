# Literature Phenotype Database

This directory is an input template for the literature-constrained
computational phenotype calibration framework.

The CSV is intentionally empty. Researchers may add records only after
extracting values from traceable sources and recording the assay context,
units, model/genotype, sample size, uncertainty, quality score, and evidence
level. Missing values must remain blank; the tooling never imputes them.

The records describe reported phenotypes. They are not biological ground truth,
clinical thresholds, or evidence that a FlyGym condition represents disease.
Compatibility with a simulation metric must be reviewed by the research team
before a record is used as a numeric calibration target.

Validate the template with:

```bash
python scripts/validate_calibration.py \
  --literature research/literature/phenotype_database.csv \
  --metrics path/to/archived_metrics.json
```

The command does not run FlyGym and does not generate scientific data.
