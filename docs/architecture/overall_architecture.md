# Overall Architecture

## Layers

1. **Runtime and simulation**: FlyGym/MuJoCo adapters create and execute the
   simulation when the pinned environment is available.
2. **Observation and artifact layer**: the recorder and exporters preserve
   rollout, metadata, checksums, and viewer-pose artifacts.
3. **Research computation**: analysis, statistics, biomarker, and validation
   packages consume imported artifacts.
4. **Orchestration**: experiment, campaign, execution, and research pipeline
   modules sequence existing services and persist status.
5. **Presentation and publication**: the web viewer, reports, figures, and
   publication assets consume outputs from the lower layers.

The layers are additive. A presentation change must not silently alter the
scientific computation layer, and a report must remain traceable to its input
artifacts.

## Source of truth

- Simulation state is owned by the simulation runtime.
- Recorded observations are owned by the rollout artifact.
- Derived measurements are owned by their analysis artifact.
- Workflow status is owned by the persisted execution or experiment manifest.
- Viewer state is owned by the web workspace and viewer_pose.json input.

## Operational entry points

- scripts/check_runtime.py: read-only runtime preflight.
- scripts/run_demo.py: demonstration/smoke execution when the runtime is
  installed.
- scripts/run_research_pipeline.py: orchestration entry point for real
  datasets and configured stages.
- scripts/bootstrap.py: one-command developer preflight and next-step guide.

No entry point should create scientific data when a required runtime or dataset
is unavailable.
