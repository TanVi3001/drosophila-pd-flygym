# Dependency Graph

This is a maintenance view of the current repository. It describes data and
control dependencies, not a new architecture. The arrows are intentionally
one-way: scientific consumers read imported artifacts and do not modify the
simulation or recorder.

Mermaid view:

    flowchart LR
        S[FlyGym / MuJoCo simulation] --> R[RolloutRecorder]
        R --> E[Rollout exporter]
        E --> D[Dataset / rollout artifacts]
        D --> VE[Viewer pose exporter]
        VE --> V[Three.js viewer / static bundle]
        D --> A[Rollout analysis]
        A --> B[Biomarker layer]
        D --> X[Experiment manager]
        X --> A
        X --> B
        A --> RP[Research pipeline orchestration]
        B --> RP
        X --> RP
        RP --> RV[Research validation]
        RV --> P[Reports and publication assets]

## Boundaries

- **Simulation** owns FlyGym/MuJoCo execution. It is not a dependency of the
  browser viewer.
- **Recorder** converts runtime observations into rollout data.
- **Exporters** serialize rollout and viewer-pose artifacts.
- **Viewer** consumes viewer_pose.json; it does not compute scientific
  metrics.
- **Analysis** reads imported rollout artifacts and produces measurements.
- **Biomarkers** reads available measurements and marks unavailable inputs
  explicitly; it does not establish clinical validity.
- **Experiment manager** organizes configured runs and their artifacts.
- **Research pipeline** coordinates existing components; it must not duplicate
  their algorithms.

The canonical package dependency declarations are in pyproject.toml. The
runtime-specific dependency check is scripts/check_runtime.py.
