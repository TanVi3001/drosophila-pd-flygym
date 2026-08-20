# Computational Disease Signature

## Scope

`DiseaseSignature` is a fixed-dimensional representation of declared
locomotion summaries. It is designed to compare a literature phenotype
signature with a simulation phenotype signature. It is not a biological model,
a medical conclusion, or a molecular disease representation.

The signature package does not run FlyGym, load rollout frames, recalculate
analysis metrics, or alter biomarker formulas. It consumes summary artifacts
that already exist.

## Fields

| Field | Intended summary |
|---|---|
| `walking_speed` | Walking speed in the source unit. |
| `stride_length` | Declared stride length in the source unit. |
| `step_frequency` | Step or stride frequency with an explicit convention. |
| `pause_fraction` | Fraction of the declared observation window spent paused. |
| `heading_variance` | Variance of heading under the source coordinate convention. |
| `turning_rate` | Turning-rate summary under the source task definition. |
| `symmetry_index` | Existing symmetry summary, without recomputation. |
| `trajectory_efficiency` | Existing path-efficiency summary. |
| `orientation_stability` | Existing orientation stability summary. |
| `joint_velocity_mean` | Existing aggregate joint-velocity mean. |
| `joint_velocity_std` | Existing aggregate joint-velocity variability. |
| `com_displacement` | Existing center-of-mass displacement summary. |
| `path_length` | Existing path-length summary. |

The model has no numeric defaults. A missing source value is represented by
`unavailable`. It is never replaced by zero, a group mean, or an inferred
value. A signature can therefore be `PARTIAL` while still being useful for a
comparison on shared metrics.

## Sources

The builder reads only:

- `metrics.json`, including `scalar_metrics` and declared summary groups;
- `biomarkers.json`, including existing biomarker `value` entries;
- `rollout_summary.json` or equivalent summary JSON.

It does not read rollout frames one by one. It does not call the simulation,
analysis, or biomarker engines. Source labels and signature identifiers are
retained in the resulting JSON for traceability.

## JSON representation

```json
{
  "schema_version": 1,
  "signature_id": "example",
  "values": {
    "walking_speed": 10.0,
    "stride_length": "unavailable"
  },
  "source": ["metrics", "biomarkers"],
  "metadata": {}
}
```

The complete document contains all thirteen declared fields. This abbreviated
example only illustrates the representation; omitted values in a real
signature are explicitly serialized as `unavailable`.

## Validation

Validation checks:

- unsupported fields and dimensional mismatch;
- non-finite values;
- missing metrics;
- duplicate signature identifiers;
- inconsistent normalization metadata.

Validation reports missing information instead of silently repairing it.

## Scientific boundary

Signature similarity is a computational concordance measure under a declared
metric, normalization, and source set. It does not establish a biological
mechanism, a stage label, treatment response, or generalization beyond the
supplied summaries.
