# Repository Benchmark

This is a scope and capability comparison, not a competitive performance
claim. No external implementation was executed by this repository audit, and
no result below should be read as evidence that one system is faster or more
scientifically valid than another.

| Capability | This repository | FlyGym | NeuroMechFly | Similar locomotion pipelines |
| --- | --- | --- | --- | --- |
| Simulation | Adapter and configuration for the pinned FlyGym/MuJoCo runtime; not available in this audit environment | External reference system | External reference system | Varies by project |
| Recording | `RolloutRecorder` and JSON/CSV/NPZ export contracts | Depends on the study integration | Depends on the study integration | Varies |
| Viewer | Static pose export, bundle, and Three.js viewer | Not benchmarked here | Not benchmarked here | Varies |
| Analysis | Rollout metrics, experiment manager, biomarker summaries | Not benchmarked here | Not benchmarked here | Varies |
| Experiment management | Dataset and experiment orchestration layers | Not benchmarked here | Not benchmarked here | Varies |
| Reproducibility | Pinned package metadata, manifests, checksums, validation tooling, and CI | Not audited here | Not audited here | Varies |
| Scientific validation | Computational artifact and scope checks; no biological validation | Not audited here | Not audited here | Varies |

## Objective Measurement Policy

The repository does not currently contain a real rollout dataset, and the
local environment does not provide Python 3.12 with FlyGym 2.1.0, MuJoCo
3.9.0, and `flygym_demo`. Therefore this audit reports no timing, memory,
accuracy, or throughput comparison. Such a comparison requires the same
hardware, runtime versions, configuration, seed policy, rollout length, and
measurement protocol for every system.

## What Can Be Compared Later

Once approved real datasets and the pinned runtime are available, record:

- simulation wall time and timestep configuration;
- recorder overhead relative to simulation time;
- export and viewer-pose conversion time;
- analysis and biomarker processing time;
- peak memory and artifact disk usage;
- frame count, missing data, and validation outcomes.

These are engineering measurements. They do not establish biological or
clinical validity.

