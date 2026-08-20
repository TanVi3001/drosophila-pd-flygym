# Open Research Questions

This document lists questions for future study. It does not answer them and
does not provide biological conclusions.

## Scientific questions

1. Which locomotion-level observations can be represented consistently by the
   current computational Disease Layer?
2. Can motor-vigor perturbation alone reproduce the direction of approved
   literature targets under a fixed assay definition?
3. Which metrics are most sensitive to inter-leg coordination perturbation?
4. Do combined proxy conditions provide better holdout concordance than single
   proxy conditions?
5. Are the proposed signature parameters identifiable from the available metric
   set, or do multiple parameter vectors produce similar signatures?
6. How do action latency and movement-initiation delay interact during turning
   and movement onset?
7. Does fatigue produce a reproducible temporal trend across rollout duration
   and random seeds?
8. Can left-right asymmetry be distinguished from execution noise using
   trajectory, contact, and orientation summaries?
9. Under what operational definition can an episodic movement-arrest proxy be
   evaluated without dominating the complete signature?
10. Which target metrics remain robust when literature assays, units, or
    observation windows differ?

## Hypotheses requiring testing

- A single global action-gain perturbation may be insufficient to reproduce a
  multi-metric locomotion signature.
- Coordination perturbations may affect contact and turning metrics more
  strongly than global displacement metrics.
- Combined perturbations may improve in-sample concordance while increasing
  parameter non-identifiability.
- Stochastic execution noise may require repeated seeds before variance metrics
  can be compared responsibly.
- A literature-derived target set may contain incompatible assay definitions
  that cannot be combined into one calibration objective.
- Holdout concordance may differ from calibration concordance even when the
  calibration loss is low.

These are hypotheses, not findings.

## Missing data

The research program still needs:

- curator-approved papers and complete provenance;
- assay-compatible locomotion values with units;
- age, sex, genotype, and sample context where relevant;
- explicit definitions for stride, pause, turning, contact, and orientation;
- uncertainty or replicate-level information;
- independent holdout observations;
- real FlyGym rollout datasets under declared controller conditions;
- repeated-seed and repeated-run records;
- external biological validation data;
- a preregistered statistical protocol.

## Questions about platform validity

- Which modules will be retained in the minimum publication path after the
  first real campaign?
- Which optional interfaces should remain experimental until additional use?
- Are all summary metrics comparable across runtime versions and assay windows?
- What provenance fields are mandatory for each publication claim?
- Which negative or unavailable results must be included in the final paper?
