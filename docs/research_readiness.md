# Research Readiness Report

This is an evidence-based operational scorecard for the repository as checked
in this audit. Scores are not scientific probabilities, clinical assessments,
or publication acceptance predictions. Each score is the sum of the explicit
items below.

## Score Summary

| Area | Score | Interpretation |
| --- | ---: | --- |
| Software readiness | 80/100 | Strong packaged/tested platform; current local real-runtime preflight is incomplete |
| Scientific readiness | 50/100 | Frozen computational evidence exists; real and biological validation are absent |
| Reproducibility | 75/100 | Versions, CI, provenance, and Colab records exist; current local runtime and new datasets are incomplete |
| Publication readiness | 75/100 | Manuscript/report package and planning assets exist; study-specific data and final rerun remain |
| Open-source readiness | 90/100 | Package, CI, community files, license, and citation metadata exist; SPDX metadata should be clarified |

## Scoring Basis

### Software readiness: 80/100

- 25/25: package metadata, source layout, and test discovery are present.
- 20/20: GitHub Actions runs compile and pytest on Python 3.12.
- 15/15: runtime, demo, dataset, analysis, and viewer tooling are documented.
- 15/15: release artifacts, architecture documentation, and public API records
  are present.
- 5/25: the current local preflight is only partial: this machine uses Python
  3.13.5 and lacks FlyGym, MuJoCo, and `flygym_demo`.

### Scientific readiness: 50/100

- 25/25: frozen computational evidence and final report artifacts are present.
- 25/25: scientific scope explicitly separates simulation outputs from biology.
- 0/25: no real rollout dataset is present under `datasets/` in this checkout.
- 0/25: no external biological validation is supplied by the repository.

### Reproducibility: 75/100

- 25/25: versions, configuration, package installation, and environment checks
  are documented.
- 20/20: CI and local compile/test commands are defined.
- 15/20: manifests, hashes, provenance, and frozen reports are present, but
  new dataset-specific run manifests are not available.
- 15/15: the project context records fresh Colab reproductions for frozen
  computational checkpoints.
- 0/20: the current local machine does not pass the real-runtime preflight.

### Publication readiness: 75/100

- 25/25: manuscript source, final PDF/DOCX, manifest, and publication package
  are present.
- 20/20: figure/table manifests and reviewer/reproducibility checklists are
  present.
- 15/20: README, MIT license, and `CITATION.cff` exist; LICENSE lacks an
  explicit SPDX identifier and no DOI is declared.
- 15/15: scientific validation and reproducibility documentation are present.
- 0/20: a new study-specific dataset and final regenerated result package are
  not present.

### Open-source readiness: 90/100

- 20/25: MIT LICENSE and community files are present; SPDX text is not explicit.
- 25/25: standard package metadata and editable installation are configured.
- 20/20: CI, Markdown validation, and Pages workflows are present.
- 15/15: architecture, API, installation, archive, and submission documentation
  are present.
- 10/15: `CITATION.cff` is present with repository/version/license metadata, but
  no DOI or journal-specific preferred citation is declared.

## Readiness Decision

The repository is ready for software distribution, computational reruns in the
documented Python 3.12 environment, and continued preparation of a submission
package. It is not ready to claim biological validation or to publish a new
dataset-specific scientific result from this checkout alone.

## Required Gates Before A New Study

1. Supply and validate the approved rollout dataset.
2. Pass the runtime checker in the exact release environment.
3. Run the final analysis, biomarker, statistical, and validation workflows.
4. Archive manifests, hashes, seeds, logs, figures, tables, and reports.
5. Review all claims against the scientific boundary and external evidence.
