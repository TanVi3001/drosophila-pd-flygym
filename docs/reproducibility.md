# Reproducibility Guide

This guide describes how to recreate the computational workflow without
changing the scientific implementation.

## Supported Environment

The certified target is:

| Component | Requirement |
| --- | --- |
| Python | 3.12.x |
| FlyGym | 2.1.0 |
| MuJoCo | 3.9.0 |
| NumPy | `>=1.26` |
| PyYAML | `>=6.0` |
| Matplotlib | `>=3.8,<4` |

Test and documentation extras are declared in `pyproject.toml`. Use
`docs/runtime_environment.md` for Windows, Ubuntu, and Google Colab setup.

Check the active environment before attempting a real run:

```bash
python scripts/check_runtime.py
```

The checker is read-only. A failed check must be repaired in the active Python
environment; it will not install packages or create data.

## Dataset Structure

A real dataset is expected to be organized beneath a declared category, for
example:

```text
datasets/
  healthy/
    Healthy_001/
      rollout.json
      rollout.npz
      viewer_pose.json
      metadata.json
      manifest.json
```

The exact manifest and metadata contract is defined by the relevant dataset
preparation materials. Raw rollout files and derived artifacts must retain
their provenance and checksums. No synthetic rollout is a substitute for an
approved dataset.

## Experiment Workflow

The end-to-end computational sequence is:

```text
configuration
  -> FlyGym/MuJoCo simulation
  -> RolloutRecorder
  -> rollout export
  -> viewer pose export
  -> viewer bundle
  -> imported rollout analysis
  -> biomarker summary
  -> reports and publication assets
```

The existing entry points are:

```bash
python scripts/run_demo.py --steps 100 --no-install-simulation
python scripts/generate_research_dataset.py --count 1
python scripts/run_experiment_suite.py
```

The first two commands require the real simulation stack and only generate
data from FlyGym. The experiment suite consumes datasets that already exist; it
does not create rollouts.

## Seed Management

Seeds are declared in experiment and campaign configuration where a run
requires them. Keep the seed, configuration path, git commit, Python version,
FlyGym version, MuJoCo version, timestep, duration, and output manifest with
each run. Do not infer a seed after execution.

## Deterministic Execution

The repository context records deterministic or controlled-seed behavior for
the frozen computational baselines and paired perturbation checkpoints. That
means the documented configurations and controls were reproduced under the
recorded environments; it is not a guarantee that every operating system,
native backend, or dependency combination produces byte-identical files.

For a new run, compare both semantic metrics and artifact hashes. Record
whether timestamps, JSON serialization order, figure metadata, and native
rendering outputs are expected to vary.

## Known Sources Of Nondeterminism

- Python, NumPy, FlyGym, MuJoCo, and transitive dependency version changes;
- operating-system and native-library differences;
- physics or rendering backend behavior;
- floating-point ordering and parallel execution;
- timestamps and generated metadata in manifests and reports;
- figure rasterization and browser rendering.

Use the pinned versions, one declared seed, sequential execution, and a clean
output directory when exact reproduction is required. Preserve the original
outputs rather than overwriting an evidence artifact.

## Reproducibility Boundary

Reproduction of a computational rollout validates software and simulation
behavior only. It does not validate Parkinson's disease biology, clinical
biomarkers, or conclusions from real flies. The current checkout has no real
rollout dataset under `datasets/`, so a new dataset-dependent result cannot be
reproduced until the approved input is supplied.
