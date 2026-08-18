# Figure Manifest

This is a planning and provenance manifest. It does not create or imply any
missing figure. A figure is publication-ready only after its source artifact,
generation command, configuration, and validation record are attached.

## Manuscript Figure Plan

| ID | Figure | Status | Source | Generation path | Boundary |
| --- | --- | --- | --- | --- | --- |
| Figure 1 | Overall architecture | Planned | `docs/repository_architecture.md` | Documentation/rendering tool | Architecture diagram only |
| Figure 2 | Simulation pipeline | Planned | FlyGym adapter and workflow docs | Existing workflow documentation | Computational pipeline only |
| Figure 3 | Digital Twin workflow | Planned | Digital Twin platform docs | Existing platform artifacts | Workflow, not biological state |
| Figure 4 | Healthy trajectory | Conditional | Imported Healthy `rollout.json` | Existing analysis/viewer tools | Requires approved Healthy rollout |
| Figure 5 | Computational comparison trajectory | Not available in current checkout | Approved comparison rollouts | Existing comparison tools | No biological PD claim |
| Figure 6 | COM analysis | Conditional | Rollout COM channel or metrics | Existing analysis tools | Unavailable when COM is absent |
| Figure 7 | Speed distribution | Conditional | Imported rollout metrics | Existing analysis/statistics tools | Requires final dataset |
| Figure 8 | Biomarker radar | Conditional | Biomarker report JSON | `drosophila_pd.biomarkers` report writer | Computational composite only |
| Figure 9 | Comparison dashboard | Conditional | Multiple biomarker reports | Existing comparison/report tooling | No condition interpretation without protocol |
| Figure 10 | Viewer | Conditional | `viewer_pose.json` and static bundle | `scripts/run_demo.py` / bundle tooling | Presentation of imported data |

## Existing Frozen Evidence Figures

These are actual tracked computational outputs, not placeholders:

| Artifact | Path | Source |
| --- | --- | --- |
| E1 parameter response | `results/analysis/figures/e1_parameter_response.png` | Frozen E1 evidence synthesis |
| E2 condition comparison | `results/analysis/figures/e2_condition_comparison.png` | Frozen E2 evidence synthesis |
| E3 paired seed robustness | `results/analysis/figures/e3_paired_seed_robustness.png` | Frozen E3 evidence synthesis |
| E5 computational reversibility | `results/analysis/figures/e5_computational_reversibility.png` | Frozen E5 evidence synthesis |

## Figure Gate

Before submission, record for each figure:

- input dataset and manifest hash;
- configuration and git commit;
- exact generation command;
- output hash and dimensions;
- missing-channel handling;
- caption and scientific boundary review.

No Healthy, computational comparison, or biomarker figure should be labeled as
real biological evidence unless the corresponding approved experimental data
and external validation exist.
