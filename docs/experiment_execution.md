# Experiment Execution Checklist

Complete this checklist from generated reports and manifests. Do not mark a
step PASS because it is configured or planned.

## Runtime and Smoke Test

- [ ] Runtime PASS
- [ ] Smoke test PASS
- [ ] `Healthy_001` PASS
- [ ] Viewer PASS for the exported `viewer_pose.json`
- [ ] Validation PASS

## Batch Progress

- [ ] `Healthy_020` PASS
- [ ] PD Mild batch PASS
- [ ] PD Moderate batch PASS
- [ ] PD Severe batch PASS
- [ ] 80 datasets PASS

## Downstream Workflow

- [ ] Experiment Suite PASS
- [ ] Biomarkers PASS
- [ ] Final Validation PASS
- [ ] Paper Package PASS

## Required Gate

Run the existing orchestrator after the runtime and datasets are available:

```bash
python scripts/run_research_pipeline.py
```

The workflow must stop at the first failed gate. `WAITING_RUNTIME`,
`WAITING_DATASET`, and `FAILED` are actionable states, not successful
experimental results.

## Scope

This checklist tracks computational execution and artifact readiness only. It
does not assign disease severity, establish biological validity, or replace
external experimental validation.
