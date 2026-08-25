# Evidence scoring

## Purpose

Scoring evaluates whether a literature record contains the information needed for later review. It does not evaluate whether a Disease Layer proxy is biologically correct.

## Configurable criteria

The default policy is in `configs/evidence/default.yaml`. Each criterion contributes a binary presence value multiplied by its configured weight:

| Criterion | Default weight | Evidence checked |
| --- | ---: | --- |
| `locomotion_assay` | 18 | Named climbing, flight, crawling, geotaxis, walking or trajectory assay |
| `quantitative_metric` | 18 | Verified numeric phenotype/source-data value |
| `sample_size` | 12 | Sample size, animals, trials or experiments reported |
| `protocol` | 12 | Reproducible method details are present |
| `genotype` | 10 | Genotype/model is identified |
| `control` | 10 | Control, revertant, wild-type or comparison group is identified |
| `provenance` | 10 | Article or open-access source URL is recorded |
| `doi_pmid` | 5 | DOI or PMID is recorded |
| `supplementary` | 5 | Supplementary/source-data provenance is recorded |

The score is normalized to 0-100 after applying the configured weights. Thresholds are configurable as `high_threshold` and `medium_threshold`.

## Example configuration

```yaml
criteria:
  locomotion_assay: 20
  quantitative_metric: 30
  sample_size: 10
  protocol: 10
  genotype: 10
  control: 10
  provenance: 5
  doi_pmid: 3
  supplementary: 2
high_threshold: 80
medium_threshold: 55
```

Weights can express the review protocol's priorities, but changing weights does not create missing evidence. A record with no verified numeric outcome remains qualitative even if its provenance score is high.

## Interpretation

- `HIGH`, `MEDIUM`, and `LOW` describe evidence-record completeness only.
- `quantitative_metric=false` means no verified numeric phenotype value was found in the supplied artifacts.
- `manual_review_required=true` is retained until a human verifies the paper, figure/table, units, and provenance.
- Calibration and validation flags are copied from the reviewed mapping; the engine does not approve them.
