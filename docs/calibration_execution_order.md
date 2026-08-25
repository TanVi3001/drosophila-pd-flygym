# Calibration Execution Order

## Scope

This is an execution sequence for a future computational locomotion study. It
does not authorize simulation, create targets, or claim that any condition is
Parkinson disease. Each stage must use approved literature evidence and real
rollout artifacts only.

```text
Healthy
  -> Motor Vigor
  -> Coordination
  -> Noise
  -> Delay
  -> Fatigue
  -> Asymmetry
  -> Freezing
  -> Latency
  -> Postural Instability
```

## Stage gates

Do not start a stage until all applicable gates pass:

1. Python/FlyGym/MuJoCo runtime is available and checked.
2. Healthy rollout and artifact integrity checks pass.
3. The proxy is implemented and its metric contract is explicit.
4. An approved quantitative target exists with unit, uncertainty, assay, and
   provenance.
5. Calibration, validation, seed, and holdout policies are fixed before the
   run.
6. The previous stage's outputs are archived and its limitations are recorded.

If a gate is not met, record `WAITING_RUNTIME`, `WAITING_DATASET`, or
`WAITING_EVIDENCE` as appropriate. Do not substitute a technical sweep for a
scientific target.

## Rationale for the order

### 1. Healthy

Establish the controller, recorder, metric, and artifact baseline before any
perturbation. This separates pipeline failure from proxy response.

### 2. Motor Vigor

This is the most directly observable control-level perturbation in the current
implementation and has the largest current mapping coverage. It still needs a
quantitative approved target before calibration.

### 3. Coordination

Run after the baseline output response is characterized so that changes in
coordination metrics are not silently treated as simple speed changes. Contact,
gait, and trajectory metrics must be available.

### 4. Noise

Noise should be evaluated after deterministic response behavior is recorded.
Use repeated seeds and a preregistered variance definition; do not label
variance as tremor or a biological mechanism.

### 5. Delay

Delay requires a clear episode start and initiation-time contract. It follows
the metric baseline because timing effects cannot be interpreted from a single
aggregate speed value.

### 6. Fatigue

Fatigue requires a sufficiently long or repeated protocol and a time-resolved
metric. It should not be inferred from an age effect or from one short rollout.

### 7. Asymmetry

Run only after left/right joint identity, sign convention, pairing, and
symmetry metrics are verified on real artifacts.

### 8. Freezing

Run only after an operational freezing definition exists, including speed
threshold, minimum duration, and event handling. Reduced activity alone is not
freezing.

### 9. Latency

Run after action/sensor timestamps and the latency field are implemented and
validated. Completion time must not be used as an unseparated latency target.

### 10. Postural Instability

Run after orientation/COM stability metrics and the proxy implementation are
available. A morphology or climbing observation is not a substitute for a
postural trajectory measurement.

## Reporting after each stage

Archive configuration, seeds, runtime report, dataset manifest, checksums,
metric availability, target provenance, loss definition, and holdout result.
Report `UNAVAILABLE` when a metric is absent. Reports must state that the
result is a computational locomotion response and not biological validation,
clinical prediction, diagnosis, drug response, or therapeutic validation.
