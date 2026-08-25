# Literature-to-Disease Layer Mapping Guideline

## Scope

This document defines a human-in-the-loop mapping workflow:

```text
Paper -> curated phenotype -> literature metric -> computational proxy
      -> candidate simulation metric -> calibration/validation review
```

The mapping is a research record, not an automated biological inference. It
does not establish a Parkinson disease mechanism, a clinical biomarker, or a
therapeutic response.

The working template is
`research/disease_layer_mapping/paper_proxy_mapping.csv`. Existing curation
records under `research/curation_workspace/` remain source material and must be
reviewed before they are copied into the new template.

## Required review evidence

A row should remain `PENDING_REVIEW` until the curator can identify:

- the paper and provenance (`paper_id`, DOI or PMID when available);
- the genotype, assay, age/sex context when reported, and control group;
- the phenotype definition and the exact literature metric;
- the metric unit, sample size, uncertainty/statistical description, and figure,
  table, supplement, or page reference when applicable;
- whether the endpoint is quantitative, qualitative, or not usable for a target.

`confidence` describes the strength of the mapping rationale, not the quality
of a disease diagnosis. Use `HIGH`, `MEDIUM`, `LOW`, or `NONE`. A low-confidence
mapping may be useful for a validation question but must not become a numeric
calibration target without further evidence.

## Proxy guidance

### `motor_vigor`

Use when the paper measures an overall locomotor output such as speed,
distance, climbing performance, or movement amount and the endpoint cannot be
separated into a more specific computational component. Keep climbing,
walking, larval crawling, and adult walking as separate assay contexts.

Do not map a generic statement such as “behavioral defect” without a defined
locomotion assay. Do not interpret this proxy as muscle physiology, dopamine
activity, or a clinical bradykinesia measurement.

### `coordination`

Use when the paper measures gait coordination, inter-leg timing, stepping
regularity, bilateral coordination, or a comparable movement organization
endpoint. A turning or flight result alone is only a candidate mapping unless
the protocol measures coordination directly.

Do not use a reduced speed value as coordination evidence when the assay does
not separate speed from coordination.

### `noise`

Use for a quantified within-trial or between-trial variability endpoint, such
as speed variability, trajectory variability, or action variability, when the
protocol and variance definition are explicit.

Do not call an irregular movement pattern “noise” without a defined variance
or dispersion measure. Noise is a computational perturbation, not a claim of
tremor or a neuronal mechanism.

### `delay`

Use only when movement initiation or a transition delay is measured with a
clear time origin and unit. A total task completion time is insufficient unless
the initiation component is separately identified.

### `fatigue`

Use only for a time-dependent decline measured across a defined duration,
repeated trials, or longitudinal protocol. Age-related decline by itself is
not enough to map fatigue.

### `latency`

Use only when an action, sensory, or response latency is operationally defined
and separated from walking speed, execution time, and task duration. Do not
derive latency from a single climbing completion time.

### `freezing`

Use only when the paper defines an arrest event or immobility episode with a
threshold and minimum duration. “Idling”, “reduced activity”, or a low average
speed is not automatically freezing.

### `asymmetry`

Use only when left/right or bilateral measurements are reported with a known
side convention. Record the side labels and pairing rule. Do not infer
laterality from an unlabelled trajectory or from an aggregate score.

### `postural_instability`

Use for an explicit posture, orientation, balance, COM, or body-stability
endpoint. A climbing defect or flight-muscle phenotype must not be mapped to
postural instability unless posture/stability is measured directly.

## When not to map

Leave `proxy` empty or use a documented unmapped review state when:

- the paper has no locomotion or movement endpoint;
- the phenotype is morphological, cellular, molecular, or treatment-only with
  no compatible movement measure;
- the assay context is incompatible with the proposed simulation metric;
- the paper does not provide enough provenance to identify the observation;
- the mapping would require inventing a unit, direction, sample size, or
  numerical value;
- the proposed relation is only a biological hypothesis and is not a measured
  phenotype.

## Review states

Use a controlled value in `review_status`:

- `PENDING_REVIEW`: entered for curator review, not approved;
- `NEEDS_DATA`: source exists but a required context or value is missing;
- `APPROVED_MAPPING`: mapping rationale and provenance passed manual review;
- `REJECTED_MAPPING`: mapping is not supported or is out of scope.

Only an `APPROVED_MAPPING` with an approved quantitative target may be copied
to `research/simulation_targets.csv`. Approval of a mapping does not by itself
approve a calibration value.

## Scientific boundary

The Disease Layer is a computational locomotion perturbation model. It does
not simulate dopamine neurons, a neural connectome, alpha-synuclein biology,
cell death, clinical diagnosis, or drug response. Every mapping must preserve
the distinction between a measured paper phenotype and a computational proxy.
