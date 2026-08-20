# Computational Disease Layer v2

## Scientific status

This document specifies a **biologically informed computational motor-control
perturbation model**. It is not a biological Parkinson model, a neural
connectome, a dopamine simulation, or a disease-severity estimator.

The Disease Layer is a declared transformation between an existing healthy
controller and the action interface used by the simulation. Its parameters are
computational proxies. They may be compared with literature-derived
locomotion observations only through an explicit, curator-reviewed calibration
protocol. A parameter value is not a measurement of a neuron, neurotransmitter,
gene expression level, disease stage, or clinical state.

No numerical biological target, threshold, or expected effect size is defined
here. Those values must come from approved literature records or new
experimental data and must retain their provenance.

## 1. Purpose and design principles

The layer is intended to make controller perturbations:

- explicit and inspectable;
- composable without changing the healthy controller;
- reproducible under a recorded random seed;
- separable from the FlyGym and MuJoCo simulation core;
- calibratable against declared locomotion endpoints;
- falsifiable through holdout conditions and external validation.

The model uses phenomenological transformations of controller output and
controller state. It does not claim that a transformation is the mechanism
that causes a biological phenotype.

## 2. Architecture

```text
Healthy Controller
        |
        v
Computational Disease Layer
  - vigor
  - coordination
  - initiation delay
  - execution noise
  - fatigue
  - asymmetry
  - freezing gate
  - action latency
  - postural-stability proxy
        |
        v
Action Modifier
        |
        v
FlyGym action interface
        |
        v
Locomotion rollout
        |
        v
Metrics and biomarkers
        |
        v
Calibration and validation
```

The action modifier is the sole runtime boundary. It receives the healthy
controller action and the declared layer state, applies the configured
transformation, and returns an action in the existing action contract. The
layer must not mutate simulation physics, invent observations, or bypass the
recorder.

Each rollout should record:

- the complete parameter vector;
- the parameter interpretation and normalization convention;
- the random seed, if a stochastic component is enabled;
- the controller and simulation configuration identifiers;
- the layer state transitions relevant to the rollout;
- the calibration target provenance, when calibration is performed.

## 3. Proxy specification

The following specifications describe design hypotheses, not observed results.

### 3.1 Motor vigor reduction

| Field | Specification |
|---|---|
| Name | Motor vigor reduction |
| Description | Reduces the magnitude of selected locomotor action commands while preserving the healthy controller topology. |
| Biological motivation | Reduced movement vigor is a reported locomotor phenotype that can motivate a computational perturbation. It does not identify a biological cause. |
| Computational proxy | A bounded gain applied to the declared action components. |
| Expected locomotion effect | Lower action amplitude may reduce translational output and joint excursion; the direction and magnitude must be measured per controller and task. |
| Affected metrics | Walking speed, stride length, joint velocity, COM displacement, turning response. |
| Calibratable | Yes, when target metrics and units are available with provenance. |
| Parameters | `motor_vigor` and the action-component mask. |
| Limits | Cannot represent neural mechanism, muscle mechanics, or a unique biological interpretation. |

### 3.2 Inter-leg coordination loss

| Field | Specification |
|---|---|
| Name | Inter-leg coordination loss |
| Description | Weakens or perturbs the coupling terms that coordinate leg action timing in the healthy controller. |
| Biological motivation | Altered coordination is a locomotion-level observation that may be relevant to disease phenotyping. |
| Computational proxy | A retained-coupling scale or bounded coupling perturbation applied to the controller's coordination pathway. |
| Expected locomotion effect | May alter foot-contact timing, turning consistency, stride regularity, and trajectory efficiency. |
| Affected metrics | Stride length, foot contact, turning, heading variance, joint velocity, COM oscillation. |
| Calibratable | Yes, if coordination endpoints are defined consistently between evidence and simulation. |
| Parameters | `coordination`, coupling selection, and any declared phase rule. |
| Limits | A controller coupling term is not a biological synapse or motor-circuit measurement. |

### 3.3 Movement initiation delay

| Field | Specification |
|---|---|
| Name | Movement initiation delay |
| Description | Delays the onset of a movement episode after an explicit initiation event or command. |
| Biological motivation | Delayed initiation can be a locomotion-level behavioral observation. |
| Computational proxy | A deterministic or seeded delay state before action output becomes active. |
| Expected locomotion effect | May increase initial pause duration and reduce the number of initiated movement episodes within a fixed observation window. |
| Affected metrics | Pause, walking speed over the full window, turning onset, action latency. |
| Calibratable | Yes, when episode boundaries and timing resolution are documented. |
| Parameters | `delay` and the initiation-event definition. |
| Limits | Must not be interpreted as a specific neural pathway or reaction-time measurement without evidence. |

### 3.4 Motor execution noise

| Field | Specification |
|---|---|
| Name | Motor execution noise |
| Description | Adds bounded, reproducible perturbation to the action after healthy control computation. |
| Biological motivation | Increased movement variability can motivate a computational variability proxy. |
| Computational proxy | Seeded stochastic or deterministic noise with a declared distribution, scope, and bound. |
| Expected locomotion effect | May increase trial-to-trial variability, heading variance, COM oscillation, and joint-velocity variability. |
| Affected metrics | Heading variance, orientation stability, COM oscillation, joint velocity, turning. |
| Calibratable | Yes, only when the target variance and sampling units are known. |
| Parameters | `noise`, seed, distribution, action scope, and bound. |
| Limits | Noise is not tremor, neuronal variability, or a measured biological fluctuation unless independently validated. |

### 3.5 Fatigue accumulation

| Field | Specification |
|---|---|
| Name | Fatigue accumulation |
| Description | Applies a history-dependent reduction or state change as locomotion progresses. |
| Biological motivation | Declining movement output over time can be an observable phenotype in a defined assay. |
| Computational proxy | A bounded cumulative state driven by declared action, time, or episode variables. |
| Expected locomotion effect | May produce time-dependent reductions in speed, stride length, joint velocity, or turning response and may increase pauses. |
| Affected metrics | Walking speed trend, stride length trend, pause, joint velocity, orientation stability. |
| Calibratable | Yes, when longitudinal measurements and assay duration are available. |
| Parameters | `fatigue`, accumulation rule, recovery rule, and state bounds. |
| Limits | Does not model energy metabolism, muscle physiology, or biological exhaustion. |

### 3.6 Left-right asymmetry

| Field | Specification |
|---|---|
| Name | Left-right asymmetry |
| Description | Applies a signed difference between corresponding left and right action groups. |
| Biological motivation | Side-specific locomotion differences may be observed in some experimental conditions. |
| Computational proxy | A bounded antisymmetric gain or offset with an explicit left/right mapping. |
| Expected locomotion effect | May bias turning direction, contact timing, stride symmetry, and heading stability. |
| Affected metrics | Turning, stride length, foot contact, heading variance, COM oscillation, orientation stability. |
| Calibratable | Yes, if the side convention and asymmetry metric are specified. |
| Parameters | `asymmetry`, affected body groups, sign convention, and side mapping. |
| Limits | Does not identify lesion laterality, unilateral pathology, or biological cause. |

### 3.7 Freezing probability

| Field | Specification |
|---|---|
| Name | Freezing probability |
| Description | Gates or interrupts action output according to a declared state-transition rule. |
| Biological motivation | Episodic movement arrest can be an assay-level observation requiring careful operational definition. |
| Computational proxy | A bounded event probability or hazard scale with a seeded state machine and explicit release rule. |
| Expected locomotion effect | May increase pause duration, reduce displacement, interrupt turning, and create discontinuities in movement episodes. |
| Affected metrics | Pause, walking speed, turning, trajectory curvature, foot contact, action latency. |
| Calibratable | Yes, only when freezing is operationally defined and annotated in the target evidence. |
| Parameters | `freezing`, trigger rule, minimum duration, release rule, and seed. |
| Limits | A stochastic gate is not a claim that a biological freezing mechanism is present. |

### 3.8 Action latency

| Field | Specification |
|---|---|
| Name | Action latency |
| Description | Delays application of an already computed action relative to the controller time at which it was produced. |
| Biological motivation | A response lag may be measurable in a defined sensorimotor assay. |
| Computational proxy | A bounded action buffer or delayed-action queue. |
| Expected locomotion effect | May reduce rapid turning responsiveness, alter contact timing, and increase trajectory error during changes in direction. |
| Affected metrics | Turning, heading variance, foot contact, joint velocity, orientation stability. |
| Calibratable | Yes, when controller and observation timestamps are aligned. |
| Parameters | `latency`, buffer policy, interpolation policy, and timestep. |
| Limits | Must be distinguished from movement initiation delay; it is not automatically a neural conduction delay. |

### 3.9 Postural instability

| Field | Specification |
|---|---|
| Name | Postural instability proxy |
| Description | Reduces the retained strength or precision of a declared stabilizing action component. |
| Biological motivation | Instability of body orientation or support can be an observable locomotion endpoint. |
| Computational proxy | A retained stability gain, bounded corrective-action attenuation, or controlled perturbation to stabilization. |
| Expected locomotion effect | May increase orientation variance, COM oscillation, heading variance, and corrective joint activity. |
| Affected metrics | Orientation stability, heading variance, COM oscillation, joint velocity, foot contact. |
| Calibratable | Yes, when body orientation and COM measurement conventions are fixed. |
| Parameters | `stability`, stabilizer selection, correction bound, and reference frame. |
| Limits | Does not model vestibular, sensory, muscular, or neural postural mechanisms. |

## 4. Parameter vector

The proposed vector is:

```text
theta = {
    motor_vigor,
    coordination,
    delay,
    noise,
    fatigue,
    asymmetry,
    freezing,
    latency,
    stability
}
```

The following convention keeps the healthy identity explicit:

| Parameter | Range | Healthy default | Meaning | Interaction | Expected sensitivity |
|---|---|---|---|---|---|
| `motor_vigor` | `[0, 1]` retained gain | `1` | Fraction of declared healthy action magnitude retained. | Interacts with fatigue, freezing, and asymmetry. | Often direct for speed and stride, but controller-dependent. |
| `coordination` | `[0, 1]` retained coupling | `1` | Fraction of the selected coordination pathway retained. | Interacts with asymmetry, latency, and contact timing. | Often strongest for regularity and contact metrics. |
| `delay` | `[0, 1]` normalized impairment | `0` | Scale of movement-initiation delay within the configured assay bounds. | Can compound with latency and freezing. | Sensitive to episode definition and observation window. |
| `noise` | `[0, 1]` normalized intensity | `0` | Scale of the declared execution-noise process. | Interacts with stability and asymmetry. | Primarily affects variance metrics; seed-sensitive. |
| `fatigue` | `[0, 1]` accumulation rate | `0` | Rate at which the declared fatigue state changes controller output. | Interacts with duration, vigor, and recovery. | Sensitive to rollout duration. |
| `asymmetry` | `[0, 1]` normalized side difference | `0` | Magnitude of signed left-right action difference. | Interacts with coordination and stability. | Sensitive to side mapping and turning task. |
| `freezing` | `[0, 1]` event/hazard scale | `0` | Scale of the declared freezing transition rule. | Interacts with delay, latency, and fatigue. | Sensitive to episode annotations and seed. |
| `latency` | `[0, 1]` normalized action delay | `0` | Scale of the action buffer delay. | Interacts with coordination and stability. | Sensitive to timestep and rapid maneuvers. |
| `stability` | `[0, 1]` retained stabilizing gain | `1` | Fraction of the selected stabilizing action retained. | Interacts with noise, asymmetry, and coordination. | Sensitive to body-frame and COM definitions. |

The ranges above are computational normalization conventions, not biological
reference ranges. A project may use a different bounded mapping only if it is
recorded in the manifest and held fixed during calibration. A calibration run
must not silently change parameter semantics between training, validation, and
holdout conditions.

## 5. Qualitative locomotion hypotheses

The table below is a hypothesis matrix for experiment design. It contains no
measurements and must not be read as a result table.

| Proxy | Walking speed | Stride length | Turning | Pause | Heading variance | COM oscillation | Foot contact | Joint velocity | Orientation stability |
|---|---|---|---|---|---|---|---|---|---|
| Motor vigor reduction | May decrease | May decrease | May reduce response | May increase indirectly | May change through reduced correction | May change through reduced support | May alter contact force/timing proxy | May decrease | May decrease if corrections are weakened |
| Coordination loss | May become less efficient | May become less regular | May become less consistent | May increase after coordination disruption | May increase | May increase | May desynchronize | May become less regular | May decrease |
| Initiation delay | Lower over a fixed window | Not necessarily changed after onset | Later turning onset | Increase at episode start | Not necessarily changed after onset | Not necessarily changed after onset | Delayed onset | Delayed onset | Not necessarily changed after onset |
| Execution noise | May become more variable | May become more variable | May become less precise | May increase if control is interrupted | May increase | May increase | More variable timing | More variable | May decrease |
| Fatigue accumulation | May decline over time | May decline over time | May decline late in the rollout | May increase over time | May increase late in the rollout | May increase or change over time | May become less regular | May decline or vary over time | May decline over time |
| Left-right asymmetry | May be direction-dependent | May differ by side | May bias one turning direction | May change during correction | May increase | May become direction-dependent | May differ by side | May differ by side | May decrease |
| Freezing probability | May decrease in the full window | May be interrupted | May be interrupted | Increase in episode duration/frequency | May increase at transitions | May show stops and restarts | May show interrupted episodes | May pause | May be unstable at transitions |
| Action latency | May decrease during maneuvers | May change during transitions | May reduce rapid response | May increase after command changes | May increase during corrections | May increase during corrections | May shift timing | May lag controller demand | May decrease |
| Postural instability | May decrease through cautious or corrective output | May become less stable | May become less precise | May increase during recovery | May increase | May increase | May show compensatory timing | May increase corrective activity | May decrease |

These are directional expectations for preregistered tests. A result that does
not match an expectation is informative about the proxy/controller pair and
must not be silently reframed as biological evidence.

## 6. Calibration target design

Calibration is a constrained comparison between approved evidence and a
simulation endpoint. It is not an automated claim that the model reproduces a
disease mechanism.

```text
Approved biological evidence
        |
        v
Declared target and uncertainty/qualitative direction
        |
        v
Mapped simulation metric with matching units and window
        |
        v
Transparent loss function
        |
        v
Candidate theta -> rollout -> metrics -> validation/holdout
```

| Target metric | Biological evidence required | Simulation metric | Loss design |
|---|---|---|---|
| Walking speed | Assay, unit, age/sex/genotype context, and provenance | Mean or episode-specific planar speed over a declared window | Unit-aware normalized discrepancy; omit target if unavailable. |
| Stride length | Operational stride definition and measurement unit | Stride-length metric from the recorded trajectory/contact data | Compare only when segmentation conventions are compatible. |
| Pause | Pause definition, threshold, and observation window | Pause fraction or pause-duration distribution | Use a declared scalar or distribution loss; do not infer missing pauses. |
| Turning | Turning assay and angular measurement convention | Turning rate, heading change, or trajectory curvature | Compare the same task and coordinate convention. |
| Heading variance | Evidence definition and reference frame | Heading variance from rollout orientation/trajectory | Use a scale-aware variance discrepancy. |
| COM oscillation | COM definition and sampling window | COM displacement/velocity/oscillation metric | Compare only after frame rate and coordinate normalization. |
| Foot contact | Contact definition and sensor/annotation protocol | Recorded contact ratio or contact duration | Require matching contact semantics; otherwise mark unavailable. |
| Joint velocity | Joint identity, coordinate convention, and unit | Joint velocity from the rollout | Match joint names, filtering, and time step. |
| Orientation stability | Body frame and orientation representation | Orientation variance or angular stability metric | Compare in a common frame; avoid quaternion-order assumptions. |

A generic transparent objective can be written as:

```text
L(theta) = sum over available metrics of
           weight(metric) * discrepancy(simulation(metric, theta), target(metric))
           + declared regularization(theta)
```

Weights, discrepancy functions, regularization, uncertainty handling, and
stopping rules must be declared before a calibration run. Missing or
incompatible targets are excluded and reported as unavailable; they are never
imputed. A calibration score measures computational concordance with the
declared targets, not biological validity.

Recommended validation layers are:

1. controller and action-contract validation;
2. rollout integrity validation;
3. within-condition repeatability under recorded seeds;
4. calibration-set response assessment;
5. holdout metric assessment;
6. sensitivity and interaction analysis;
7. external biological validation, which is outside the current repository.

## 7. Scientific boundary

The Disease Layer does **not** simulate or establish:

- dopamine neurons, dopamine concentration, or neurotransmitter dynamics;
- a neural connectome or biologically complete central pattern generator;
- alpha-synuclein aggregation;
- neuronal cell death or neurodegeneration;
- gene expression, mutation effects, or molecular pathways;
- synaptic plasticity or pharmacological action;
- drug pharmacokinetics or pharmacodynamics;
- disease onset, progression, staging, or severity;
- clinical diagnosis, clinical prediction, or treatment response;
- equivalence between a controller parameter and a biological lesion;
- equivalence between a computational phenotype and a real-fly phenotype.

The model can test whether declared action transformations produce declared
changes in simulated locomotion metrics. It cannot establish that the
transformation is the cause of a biological observation. The words
“Parkinson-like” or “disease condition” may be used only as clearly labeled
computational experiment names, never as evidence of a biological disease
state.

## 8. Research questions

These questions are proposed for future experiments and are not answered by
this specification:

1. Can motor-vigor reduction alone reproduce the direction of approved
   locomotion targets under a fixed assay definition?
2. Which metrics are most sensitive to inter-leg coordination loss in the
   selected controller?
3. Does a combined perturbation explain target patterns better than any single
   proxy while remaining identifiable on holdout conditions?
4. How does action latency interact with coordination loss during turning?
5. Does fatigue accumulation produce a stable temporal trend or only a
   controller-specific transient?
6. Can left-right asymmetry be distinguished from execution noise using the
   available trajectory and contact metrics?
7. Under what operational definition does a freezing gate improve concordance
   without dominating all other metrics?
8. Which calibration targets remain robust across random seeds and rollout
   durations?
9. Are the proposed parameters identifiable, or do multiple parameter vectors
   produce indistinguishable metric profiles?
10. Which external biological measurements are necessary before any biological
    interpretation can be evaluated?

## 9. Publication positioning

### Novelty

The proposed contribution is a transparent calibration framework for
literature-constrained, biologically informed motor-control perturbations in a
fly locomotion simulation. The novelty claim is the explicit separation of
healthy control, disease-layer transformations, action modification, metric
evaluation, and calibration provenance. It is not a claim of a new biological
mechanism.

### Contribution

The framework contributes:

- a modular vocabulary for locomotion-level computational perturbations;
- a parameter vector with explicit semantics and healthy identity defaults;
- a reproducible action-modification boundary;
- a target-to-metric mapping protocol with unit and provenance checks;
- calibration, holdout, and sensitivity-analysis requirements;
- a scientific boundary that prevents computational outputs from being
  presented as clinical or mechanistic evidence.

### Scientific scope

The immediate scope is simulation-based characterization of how controlled
motor-output transformations affect locomotion. The framework may support
hypothesis generation and software-reproducible comparisons. It does not
replace experimental animals, biological datasets, or domain-specific
validation.

### Limitations

- The proxy definitions are phenomenological and may be non-identifiable.
- The healthy controller and action space constrain the reachable phenotype.
- Metric compatibility across literature sources may be incomplete.
- Stochastic proxies require seed control and repeated evaluation.
- Qualitative concordance does not establish causal or mechanistic equivalence.
- No external biological validation is supplied by this document.

### Future work

Future work may add experimentally justified controller interfaces, curated
target records, preregistered calibration studies, independent holdout data,
and wet-lab validation. Molecular, neural, and pharmacological models should
only be introduced as separate research programs with their own evidence and
validation boundaries.

## 10. Roadmap

```text
Scientific Design
        |
        v
Implementation of the declared action modifier
        |
        v
Calibration against approved, provenance-complete targets
        |
        v
Validation: integrity, repeatability, holdout, sensitivity
        |
        v
Publication with computational scope and limitations stated explicitly
```

### Stage A: Scientific design

- Freeze proxy definitions and parameter semantics.
- Define assay windows, units, coordinate frames, and contact conventions.
- Curate literature candidates through human review.
- Predeclare targets, weights, exclusions, and validation splits.

### Stage B: Implementation

- Implement only the declared action/state transformations.
- Preserve the healthy controller and existing simulation API.
- Record parameter manifests, seeds, and layer state transitions.
- Add contract tests for identity, bounds, determinism, and composition.

### Stage C: Calibration

- Run the healthy identity condition first.
- Evaluate one-proxy and interaction conditions.
- Fit only to available, compatible targets.
- Record all candidate parameter vectors and objective components.

### Stage D: Validation

- Repeat selected conditions under declared seeds.
- Evaluate holdout targets not used for fitting.
- Report sensitivity, identifiability, missing data, and failure cases.
- Keep computational concordance separate from biological validation.

### Stage E: Publication

- Publish parameter definitions and source provenance.
- Include the full metric mapping and exclusions.
- Report negative and unavailable results.
- State that the output is a computational motor-control perturbation model,
  not a biological Parkinson model or clinical tool.

## 11. Remaining work

This document is a scientific design specification only. It does not implement
the Disease Layer v2, create rollouts, add biological evidence, or answer the
research questions. Before implementation, the project still needs:

- owner-approved parameter semantics and action masks;
- a formal interface contract with the healthy controller;
- curator-approved literature targets with units and provenance;
- preregistered calibration and holdout protocols;
- runtime and reproducibility tests for stochastic components;
- independent biological validation before any biological interpretation.

