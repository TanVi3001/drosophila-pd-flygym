# Sprint 2 Risk Register

| Risk | Cause | Impact | Detection | Mitigation |
| --- | --- | --- | --- | --- |
| Runtime risk | Unsupported Python or missing FlyGym/MuJoCo components | Simulation cannot start or may be uncertified | `scripts/check_runtime.py` | Use the pinned Python 3.12/FlyGym 2.1.0/MuJoCo 3.9.0 environment and stop at `WAITING_RUNTIME`. |
| Dataset corruption | Truncated JSON/NPZ, invalid values, or incomplete copy | Invalid metrics, viewer pose, or reports | Dataset validation and integrity reports | Use staged generation, checksums, manifest verification, and reject invalid datasets. |
| Interrupted execution | Kernel, process, or machine stops during a batch | Partial dataset or repeated work | Per-dataset status, missing-artifact checks, and logs | Resume only complete datasets; retry incomplete work after validation. |
| Storage exhaustion | Large rollout, figure, report, or duplicate artifact volume | Write failures and incomplete campaign | Filesystem capacity checks and failed artifact writes | Monitor storage, retain manifests, and allocate output storage before batch execution. |
| Version mismatch | Runtime/package/config version differs from provenance | Non-comparable or unreproducible outputs | Runtime report, metadata, and manifest provenance | Pin versions and record environment metadata for every campaign. |
| Missing dependencies | Optional analysis, validation, or export dependency unavailable | Downstream stage cannot complete | Import checks and stage error reports | Install from the declared project extras in the target environment; do not silently substitute. |
| Scientific interpretation risk | Computational labels or metrics treated as biological conclusions | Overclaiming beyond simulation evidence | Documentation review and scientific-boundary scan | Use computational wording, preserve limitations, and require external biological evidence. |

Risks are operational controls. They do not imply that an unobserved failure or
biological effect has occurred.
