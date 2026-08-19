# Research Dataset Generation

Dataset generation is an execution step for real FlyGym rollouts. It does not
create placeholders, synthetic scientific evidence, or empty result files.

## Dataset Groups

The existing generator organizes requested datasets into these groups:

- `healthy/Healthy_001` through `Healthy_020`
- `pd_mild/PD_Mild_001` through `PD_Mild_020`
- `pd_moderate/PD_Moderate_001` through `PD_Moderate_020`
- `pd_severe/PD_Severe_001` through `PD_Severe_020`

The default request is 20 datasets per group, for 80 datasets in total. A
dataset is counted only when its real rollout and required downstream artifacts
are complete.

Each completed dataset is expected to contain the existing artifact layout,
including `rollout.json`, `rollout.npz`, `viewer_pose.json`, `manifest.json`,
`metadata.json`, metrics, reports, and figures. Biomarker outputs are written
by the existing biomarker layer under `results/biomarkers/<dataset-id>`.

## Workflow

The supported order is:

```text
runtime check
    -> generate real FlyGym rollout
    -> validate dataset artifacts
    -> analysis / experiment suite
    -> biomarkers
    -> research validation
    -> paper package
```

The one-command research orchestrator enforces these gates. A failed or
waiting stage prevents downstream stages from running.

## Commands

Check the runtime first:

```bash
python scripts/check_runtime.py
```

Generate or resume the default campaign:

```bash
python scripts/generate_research_dataset.py --count 20
```

Run the gated workflow after generation:

```bash
python scripts/run_research_pipeline.py
```

The generator resumes completed datasets by default. Existing complete
datasets are not overwritten; incomplete datasets are processed according to
the existing generator's validation and error handling.

## Waiting and Failure States

- `WAITING_RUNTIME`: FlyGym, MuJoCo, or another required runtime component is
  unavailable.
- `WAITING_DATASET`: no valid real rollout is available, or dataset validation
  has not passed.
- `FAILED`: the existing execution, analysis, biomarker, or validation stage
  reported an error.

No state causes the system to invent a rollout or infer a biological result.
Inspect the generated status and validation reports before retrying.
