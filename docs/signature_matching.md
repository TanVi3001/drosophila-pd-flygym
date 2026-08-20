# Signature Matching Workflow

## Purpose

The matcher ranks supplied simulation signatures against one supplied
literature signature. It is a deterministic comparison layer, not an
optimizer and not a simulation runner.

```text
Literature signature
        |
        v
Declared normalization
        |
        v
Simulation signatures
        |
        v
Distance metric
        |
        v
Computational similarity and ranking
```

The ranking is reproducible for the same inputs, normalization statistics,
distance method, and weights.

## API

```python
from drosophila_pd.signature import load_signature, match_signatures

literature = load_signature("research/signatures/literature.json")
simulation = load_signature("datasets/healthy/Healthy_001")

report = match_signatures(
    literature,
    [simulation],
    distance_method="euclidean",
    normalization_method="none",
)
```

The matcher does not invoke FlyGym, reload rollout frames, run an optimizer,
or modify source artifacts.

## Normalization

Supported methods are:

- `none`: compare values in their declared units;
- `zscore`: center and scale using an explicit reference set;
- `minmax`: scale using explicit reference minimum and maximum;
- `robust`: center by reference median and scale by reference MAD;
- `healthy_baseline`: compute an explicit difference from a supplied healthy
  signature.

Reference data is required for methods that need it. Constant or unavailable
reference fields remain `unavailable`; no artificial spread is introduced.
Units and metric definitions must be compatible before normalization is used.

## Similarity

The current similarity transform is the transparent computational transform

```text
similarity = 1 / (1 + distance)
```

It is only a convenient monotonic display value. It is not a probability, a
clinical estimate, or a biological severity measure.

## Outputs

The report writer creates:

- `signature_report.md`;
- `signature_similarity.csv`;
- `signature_distance_matrix.csv`;
- `ranking.json`.

Unavailable comparisons remain marked as `UNAVAILABLE` and are excluded from
the ranked list.

## Command line

```powershell
python scripts/compare_signatures.py `
  --literature research/signatures/literature.json `
  --simulation datasets/healthy/Healthy_001 datasets/pd_mild/PD_Mild_001 `
  --distance euclidean `
  --normalization none `
  --output results/signature_matching
```

The CLI accepts a standalone signature JSON or a dataset directory containing
the supported summary artifacts.

## Interpretation boundary

The output answers only: “Which supplied computational signature is closest
under this declared comparison?” It does not answer whether an organism has a
biological condition, whether a mechanism is present, or whether an
intervention is effective.
