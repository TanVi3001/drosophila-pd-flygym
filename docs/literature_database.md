# Literature Database Guide

`research/literature/phenotype_database.csv` is a blank, schema-backed input
template. It contains no invented observations.

## Required provenance

Every populated row must preserve:

- paper identifier and complete citation;
- species, genotype, gene, sex, age, temperature, and assay context;
- metric value and unit;
- sample size and available uncertainty fields;
- quality score and evidence level;
- notes about extraction, exclusions, and unit conversion.

Values from different assays or genotypes must not be treated as directly
interchangeable. A value may become a calibration target only after the
research team confirms that its metric definition, unit, and context are
compatible with the archived simulation metric.

Blank values remain blank. The loader reports zero numeric targets when the
template has not been populated.
