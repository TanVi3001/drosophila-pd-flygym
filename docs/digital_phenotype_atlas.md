# Digital Phenotype Atlas

## Purpose

The Digital Phenotype Atlas is a local knowledge base for curated literature
records used later by the calibration framework. It is not AI, a Parkinson
model, a clinical predictor, or a replacement for wet-lab evidence.

```text
Paper
  ↓
Gene
  ↓
Phenotype
  ↓
Assay
  ↓
Metric
  ↓
Evidence
```

The graph is represented by dataclasses in memory. No Neo4j or database server
is required.

## Input and parser

`src/drosophila_pd/literature/parser.py` reads local CSV, JSON, and YAML files.
It never crawls the internet. Empty templates are valid and produce zero
records.

```python
from drosophila_pd.literature import load_database

database = load_database("research/phenotype_atlas/phenotype_database.csv")
```

## Reports

`write_atlas_report()` creates coverage, missing-information, evidence-matrix,
knowledge-graph, and descriptive summary artifacts. It does not impute values
or score evidence.
