# Signature Distance Framework

## Implemented distances

### Euclidean

For shared available fields, the implementation computes the ordinary
Euclidean distance. Fields marked `unavailable` are omitted from both vectors
and reported in `shared_metrics`.

### Weighted Euclidean

Weighted Euclidean requires an explicit weight for every shared field. Weights
must be finite, non-negative, and not all zero. The framework does not invent
weights from field names or disease labels.

### Cosine

Cosine distance is `1 - cosine similarity` over shared available fields. A zero
vector is reported as unavailable because its direction is undefined.

## Explicit interfaces

The following interfaces are present but intentionally do not pretend to
implement a complete scientific method for summary signatures:

- Mahalanobis distance requires a validated covariance matrix supplied by the
  caller. Without it, the result is `UNAVAILABLE`.
- Dynamic Time Warping requires time-series inputs, while
  `DiseaseSignature` stores summary metrics. The current result is
  `UNAVAILABLE`.
- Earth Mover Distance requires distribution inputs and a declared ground
  metric. The current result is `UNAVAILABLE`.

No package outside the repository's existing numeric dependencies is required.

## Missing data policy

Distances use the intersection of available metrics. A comparison with no
shared available metric returns `UNAVAILABLE`; it never treats missing data as
zero. This policy must be reported with every ranking and considered when
comparing signatures with different coverage.

## Dimension and consistency checks

Validation reports:

- unknown fields or dimension mismatch;
- NaN and infinite values;
- missing metrics;
- duplicate signature identifiers;
- mixed normalization metadata.

The fixed field contract makes vector order deterministic. Embeddings are only
plain vectors with availability masks; the package does not apply deep
learning, PCA, UMAP, or an automatically learned representation.

## Scientific interpretation

Distance and similarity are properties of supplied computational summaries
under a declared configuration. They are not biological effect sizes,
probabilities, or evidence that two phenotypes share a mechanism. Any future
calibration must report units, provenance, reference sets, weights, exclusions,
and holdout performance separately from the distance itself.
