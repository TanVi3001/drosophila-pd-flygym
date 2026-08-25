# Evidence Engine

The Evidence Engine connects curated literature records to Disease Layer proxy coverage before calibration. It consumes:

- `disease_layer_mapping.csv`
- `paper_information.json`
- `candidate_review.csv`

It does not run FlyGym, change the Disease Layer, generate scientific values, infer biological mechanisms, or perform calibration.

## Usage

```python
from drosophila_pd.evidence import run_evidence_engine

run_evidence_engine(
    mapping_csv="research/curation_workspace/pink1/disease_layer_mapping.csv",
    paper_information_json="research/curation_workspace/pink1/paper_information.json",
    candidate_review_csv="research/curation_workspace/pink1/candidate_review.csv",
    output_dir="results/evidence",
    scoring_config="configs/evidence/default.yaml",
)
```

The output directory contains the requested CSV, JSON and Markdown artifacts. The package can also be used without writing files through `build_evidence_bundle()`.

## Data flow

```text
candidate_review.csv        paper_information.json
            \                 /
             \               /
              disease_layer_mapping.csv
                       |
                       v
                validated paper join
                       |
       configurable evidence completeness score
                       |
       coverage -> importance -> dependency matrix
                       |
             research gap and summary
```

## Output meaning

`evidence_scores.*` measures the completeness of the supplied evidence record. `coverage_report.csv` counts mapped papers and distinguishes quantitative from qualitative records. `parameter_importance.csv` ranks proxy coverage by total evidence score; it is not a biological importance ranking. `dependency_matrix.csv` preserves metric-to-proxy aggregation. `disease_layer_matrix.csv` is a confidence-adjusted evidence-support matrix; empty cells mean that no mapping record was supplied.

## Scientific boundary

Evidence scores are not disease scores, diagnostic scores, clinical predictions, or simulation parameters. A paper can be a validation candidate while still being unsuitable for calibration because its numeric outcome, unit, uncertainty, or protocol is incomplete. Manual approval remains required before a record is promoted to calibration data.
