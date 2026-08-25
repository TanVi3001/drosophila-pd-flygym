# Disease Layer proxy coverage

`coverage_report.csv` reports how often each configured proxy appears in the supplied mapping records.

## Fields

- `paper_count`: unique papers mapped to the proxy.
- `mapping_record_count`: number of phenotype-to-proxy mapping rows.
- `quantitative_paper_count`: unique papers with a verified numeric phenotype value.
- `qualitative_paper_count`: mapped papers without a verified numeric phenotype value.
- `calibration_candidate_count`: papers whose mapping is marked `true` or `conditional` for calibration.
- `validation_candidate_count`: papers whose mapping is marked `true` or `conditional` for validation.
- `coverage_status`: `no_literature`, `qualitative_only`, or `quantitative_coverage`.

## Dependency outputs

`dependency_matrix.csv` aggregates each metric-to-proxy pair with paper count, confidence and evidence score. `disease_layer_matrix.csv` presents the same relationships as metric rows and proxy columns. Its non-empty value is:

```text
mean_evidence_score * mean_confidence_weight / 100
```

This is an evidence-support value for sorting and review. It is not a biological effect size, parameter value, or causal dependency.

## Research gaps

`research_gap.md` highlights proxies with no mapped literature, qualitative-only coverage, or no marked calibration/validation candidates. Missing coverage is reported as a curation gap; it is not interpreted as absence of a biological phenomenon.
