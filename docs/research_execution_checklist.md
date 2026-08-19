# Research Execution Checklist

Use this checklist only after the runtime and data are available. A checked
item must be supported by the corresponding generated report or artifact; do
not mark an item complete from a planned configuration alone.

## Runtime and Smoke Tests

- [ ] Runtime check PASS
- [ ] Smoke test PASS
- [ ] `python scripts/run_demo.py` completed with the required runtime
- [ ] `python scripts/validate_research_workflow.py` completed for the dataset

## Required Dataset Runs

- [ ] `Healthy_001` PASS
- [ ] `PD_Mild_001` PASS
- [ ] `PD_Moderate_001` PASS
- [ ] `PD_Severe_001` PASS
- [ ] 80 datasets generated and validated

Each completed dataset must have the real rollout, viewer pose, manifest,
metadata, metrics, report, and figures required by the existing validators.

## Gated Research Workflow

- [ ] Experiment Suite PASS
- [ ] Analysis PASS
- [ ] Biomarkers PASS
- [ ] Research Validation PASS
- [ ] Paper Package PASS

Run:

```bash
python scripts/run_research_pipeline.py
```

The pipeline stops at the first failed gate. Check
`results/research_status.json`, `results/research_status.md`, and
`results/final_execution_report.md` before continuing.

## Browser and Release Checks

- [ ] Browser Viewer PASS
- [ ] Release Candidate verified

The browser check must use an exported real `viewer_pose.json`; a planning
asset or placeholder is not evidence of a completed run.

## Scientific Boundary

- [ ] Results are reported as computational measurements
- [ ] No clinical or diagnostic claim is made
- [ ] Dataset provenance and validation reports are archived
- [ ] Missing runtime/data are recorded rather than silently skipped

This checklist records execution readiness only. It is not biological
validation and does not establish clinical utility.
