# Scientific Validation

This document records what is validated by the repository as software and what
remains outside its evidence boundary. It is an audit of computational scope,
not a biological validation report.

## Software Validation

- The project is packaged with a `src` layout through `pyproject.toml`.
- The public workflow is covered by the repository test suite and the Python
  3.12 GitHub Actions job in `.github/workflows/ci.yml`.
- `python -m compileall -q src scripts tests` is the repository compile check.
- `pytest -q -rs -p no:cacheprovider` is the repository regression command.
- `scripts/check_runtime.py` checks the interpreter, declared dependencies,
  FlyGym imports, the canonical `flygym_demo` helper, configuration, and
  workflow entry points without installing packages or running simulation.

These checks validate software behavior and packaging. They do not establish
that a particular local machine has a working native MuJoCo installation.

## Architecture Validation

The implemented workflow keeps the following boundaries explicit:

```text
FlyGym/MuJoCo
    -> RolloutRecorder
    -> rollout export
    -> viewer pose export
    -> static viewer bundle
    -> imported-rollout analysis and biomarker summaries
```

The biomarker layer reads `metrics.json` and `rollout.json`. It does not import
or call the simulation, recorder, exporter, viewer, or experiment manager. A
missing input channel is represented as `unavailable` instead of being
reconstructed from an unrelated channel.

## Data Integrity Validation

The repository contains manifest, metadata, checksum, and validation support in
the dataset and execution layers. Frozen evidence reports under `results/`
record their own provenance and input hashes. Large generated payloads are
excluded by `.gitignore` unless explicitly curated.

The current checkout contains no real rollout under `datasets/`; it contains
the dataset directory README only. Therefore dataset-level integrity of a new
Healthy, computational PD, Candidate, or Control collection cannot be passed
from this checkout alone.

## Rollout Validation

The source workflow validates and exports finite rollout observations, supports
the canonical `rollout.npz` name and the legacy `rollout_arrays.npz` name, and
validates viewer-pose frame, timestamp, and quaternion constraints. Existing
integration tests skip when FlyGym or MuJoCo is unavailable rather than
fabricating a rollout.

The repository context records clean Google Colab reproductions for the frozen
Block 8.12, Milestone 8B, and Milestone C through E6 computational checkpoints.
Those records validate the stated software/simulation runs only; they are not
new execution evidence from this audit.

## Viewer Validation

The viewer bundle is a static artifact assembled from `web/`, pose data, and
the existing viewer assets. GitHub Pages deployment is defined in
`.github/workflows/deploy_pages.yml`. Browser E2E tests are present but require
their explicit E2E opt-in and a browser runtime. Viewer availability does not
convert a computational rollout into biological evidence.

## Biomarker Validation

The biomarker layer is validated at the software level by tests for:

- calculation from metrics and rollout JSON;
- fallback to an available source document;
- explicit `unavailable` values for missing channels;
- JSON, CSV, Markdown, and HTML report generation;
- one-dataset and multi-dataset side-by-side comparison.

The composite `disease_severity_score` is a normalized computational mean of
available component scores. Its formula and source are written into the
report. It is not a Parkinson's disease classifier, diagnostic score, medical
biomarker, or biological severity estimate.

## Scientific Scope

This repository currently supports:

- FlyGym and MuJoCo locomotion simulation when the pinned runtime is available;
- recording and export of computational observations;
- static visualization and viewer packaging;
- computational metrics, experiment orchestration, and biomarker summaries;
- frozen computational evidence and publication artifact packaging.

It does not currently provide:

- a Parkinson's disease diagnosis;
- a replacement for biological research or experimental fly data;
- clinical biomarker validation;
- proof that a computational proxy is a biological mechanism;
- a claim that a dataset label such as `pd` is biological Parkinson's disease.

Any publication must preserve these boundaries and cite the exact generated
artifacts, configuration, software versions, and dataset provenance used for
the reported result.
