# Table Manifest

This manifest identifies tables needed for a publication and distinguishes
existing computational evidence from tables that require a future approved
dataset. It does not fill missing values.

| ID | Table | Status | Source | Required contents |
| --- | --- | --- | --- | --- |
| Table 1 | Simulation parameters | Available as configuration inputs | `configs/experiments/`, `configs/v2/flygym/` | Python/FlyGym/MuJoCo versions, timestep, duration, seed, controller and world settings |
| Table 2 | Metrics | Conditional | Imported rollout `metrics.json` and analysis outputs | Dataset-level locomotion and trajectory metrics with units |
| Table 3 | Biomarkers | Conditional | `biomarkers.json` | Biomarker values, status, units, formulas, source files |
| Table 4 | Experiment design | Available as planning material | `experiments/`, campaign/configuration files | Conditions, seeds, replicates, expected outputs, validation profile |
| Table 5 | Statistical results | Not complete for a new study | Existing statistical modules plus final dataset | Test, estimate, interval, effect size, correction, missing-data policy |
| Table 6 | Reproducibility metadata | Available as schema/support | Manifests, reports, `CITATION.cff`, environment records | Commit, versions, hashes, seeds, timestamps, artifact paths |

## Table Gate

Every final table must record its input manifest, generation command, units,
rounding policy, missing values, and artifact hash. Tables must not report a
biological interpretation that is absent from the source evidence. A `pd`
label in a computational configuration is not evidence of biological
Parkinson's disease.
