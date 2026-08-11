# Session Mapping

The v2 behavioral platform becomes the canonical implementation target for
Sessions 03-04.

## Session 03

Session 03 should use `RolloutData`, `measure_rollout_behavior()`, and
`export_rollout_package()` to convert existing rollout arrays into reproducible
behavioral measurement packages.

Expected Session 03 focus:

- construct rollout packages from already-generated simulations
- compute walking, pause, freezing, turning, trajectory, and exploration
  metrics
- export CSV, JSON, NPZ, and PNG artifacts
- document thresholds and input arrays

## Session 04

Session 04 should use comparison and visualization APIs to inspect condition
families without changing perturbation logic.

Expected Session 04 focus:

- compare Healthy, Candidate, and Rescue rollout packages
- build synchronized side-by-side playback plans
- render offline PNG sequences or videos from existing frames or trajectories
- inspect trajectory, heading, COM, joint, adhesion, and timeline overlays

## Boundary

Sessions 03-04 should not modify v1 evidence, manuscript content, release
artifacts, or scientific conclusions. Biological interpretation requires a
separate authorized evidence layer.
