# Module Responsibilities

| Area | Responsibility | Must not do |
| --- | --- | --- |
| flygym_adapter | Adapt the pinned FlyGym API and record runtime observations | Change FlyGym or invent physics |
| viewer_export | Convert valid rollout artifacts to viewer-pose data | Re-run simulation or infer missing science |
| analysis | Compute configured measurements from imported rollouts | Diagnose disease |
| biomarkers | Aggregate available metrics with explicit availability | Claim clinical validity |
| experiment_manager | Organize configured experiment inputs and outputs | Replace analysis algorithms |
| research_pipeline | Sequence existing stages and gates | Duplicate subsystem logic |
| scientific_validation | Verify integrity and reproducibility conditions | Manufacture reference data |
| web | Display viewer data and interaction state | Become a scientific data store |
| scripts | Provide thin operational entry points | Hide core domain behavior |

When a change appears to cross two rows, prefer an explicit artifact or narrow
adapter over a new shared global state. Preserve existing public APIs unless a
compatibility issue is demonstrated.
