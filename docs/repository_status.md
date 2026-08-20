# Repository Status Audit

## Audit scope

This is a documentation-only audit of the current working tree. The audit
reviews package layout, scripts, tests, existing architecture documentation,
and runtime/data gates. A reference in a test or source file is evidence of a
software contract, not evidence that a module has been used on a real
experiment.

The repository currently contains a broad platform surface: simulation
integration, artifact analysis, browser presentation, literature curation,
calibration, signature matching, orchestration, and research documentation.
The absence of FlyGym/MuJoCo or real research datasets in a local environment
remains a separate execution blocker.

## Classification criteria

- **Production Ready**: stable software contract, regression coverage, and a
  bounded responsibility. This label describes software readiness only; it is
  not a scientific or biological validation claim.
- **Research Ready**: usable for the planned research workflow once the pinned
  runtime, curated sources, and real datasets are available.
- **Experimental**: additive, optional, interface-only, or not yet demonstrated
  in a complete real-data study.
- **Deprecated**: explicitly retired or superseded by repository policy.

## Production Ready

| Area | Location | Evidence and boundary |
|---|---|---|
| Packaging and import contract | `pyproject.toml`, `src/drosophila_pd/` | Editable-install and import tests exist. |
| Healthy controller construction | `src/drosophila_pd/controllers/` | Controller/configuration contracts and regression tests exist. |
| Experiment definitions and frozen runners | `src/drosophila_pd/experiments/` | Existing experiment and perturbation tests cover declared computational behavior. |
| Generic perturbation interfaces | `src/drosophila_pd/perturbations/` | Explicit bounded interfaces are tested; they are not biological mechanisms. |
| Locomotion measurement utilities | `src/drosophila_pd/metrics/` | Measurement and assay tests exist for imported/computational artifacts. |
| Release and validation contracts | `tests/`, `.github/`, `docs/` | Compile, regression, packaging, and release-contract coverage exists. |

This classification means the software boundaries are sufficiently stable for
the declared use. It does not mean that the scientific outputs have been
validated against external biological experiments.

## Research Ready

These areas are the intended path for a real literature-driven study, subject
to their stated gates:

| Area | Location | Current gate or limitation |
|---|---|---|
| FlyGym integration and rollout capture | `src/drosophila_pd/flygym_adapter/` | Requires the pinned Python/FlyGym/MuJoCo runtime and a real run. |
| Dataset discovery and registration | `src/drosophila_pd/dataset_adapter/`, `dataset_registry/` | Requires real datasets and verified manifests/checksums. |
| Rollout and viewer export | `src/drosophila_pd/viewer_export/`, `web/` | Requires valid rollout artifacts; browser/runtime checks remain environment-dependent. |
| Imported rollout analysis | `src/drosophila_pd/analysis/`, `metrics/` | Ready for artifacts; no biological interpretation is supplied. |
| Biomarker summaries | `src/drosophila_pd/biomarkers/` | Computes declared computational summaries; external biological validation is absent. |
| Literature Atlas and curation | `src/drosophila_pd/literature/`, `literature_assistant/` | Templates and review contracts exist; real papers and curator approvals are absent. |
| Signature matching | `src/drosophila_pd/signature/` | Ready for supplied signatures; real literature signatures are not populated. |
| Calibration | `src/drosophila_pd/calibration/` | Requires approved targets, units, provenance, and a frozen holdout protocol. |
| Scientific validation | `src/drosophila_pd/scientific_validation/` | Artifact/reproducibility validation exists; external biological validation remains open. |
| Experiment and research orchestration | `experiment_manager/`, `experiment_runtime/`, `research_execution/`, `research_pipeline/` | Dataset/runtime gates stop execution when prerequisites are absent. |
| Campaign and kernel orchestration | `campaign/`, `research_campaign/`, `research_kernel/` | Orchestration contracts are present; real campaign execution is not demonstrated here. |

## Experimental

The following areas should be treated as additive or experimental until they
are exercised in a complete real-data study and their ownership is confirmed:

| Area | Location | Reason |
|---|---|---|
| Extended behavior and automation platform | `behavior_platform/`, `automation/` | Broad additive surface with optional services and multiple artifact paths. |
| Digital twin platform | `digital_twin_platform/` | Snapshot/session abstractions are tested, but real rollout-backed use is not established. |
| Research assistant | `research_assistant/` | Orchestration-facing assistance layer; not part of the minimum scientific path. |
| Legacy/compatibility Parkinson package | `parkinson/` | Retained computational interfaces require explicit study ownership before use. |
| Optional 3D/Fly Studio surfaces | `flystudio/`, `web/` | Contract-tested presentation layer; browser assets and real pose coverage remain environment-dependent. |
| Interface-only distance methods | `signature/distance.py` | Mahalanobis requires supplied covariance; DTW and Earth Mover require data types not stored by the summary signature. |
| Future calibration optimizers | `calibration/optimizer.py` | Some optimizer entries are explicitly interface-only. |

Experimental does not mean broken. It means the project should not use the
area as a central scientific dependency without an owner-approved protocol and
an execution record.

## Deprecated

No package or public API is explicitly marked deprecated in the current
repository audit. Historical milestone scripts and archived documents should
not be treated as deprecated automatically; each needs an owner decision before
removal or replacement.

## Usage audit

Textual reference scanning found at least one reference for every top-level
package under `src/drosophila_pd/` in source, tests, or scripts. Therefore no
top-level package can be honestly classified as wholly "never used" based on
the current checkout.

The following use cases are **not demonstrated** by repository references
alone:

- a successful FlyGym/MuJoCo run in the current environment;
- a complete study over real rollout datasets;
- a curated paper registry with approved phenotype records;
- calibration against real literature values;
- external biological validation;
- publication claims supported by new experimental results.

## Pipeline status

```text
Healthy Controller
        |
        v
Disease Layer
        |
        v
Simulation / FlyGym
        |
        v
Recorder
        |
        v
Analysis
        |
        v
Biomarkers
        |
        v
Computational Signature
        |
        v
Calibration
        |
        v
Validation
        |
        v
Publication planning and artifacts
```

The graph describes existing responsibilities. It does not authorize a new
workflow or imply that every downstream stage has real input data.

## Audit conclusion

The software platform is sufficiently organized to begin controlled research
data intake. The principal remaining blockers are external: pinned runtime
availability, real rollouts, curator-approved literature, defensible target
mapping, and independent scientific validation.
