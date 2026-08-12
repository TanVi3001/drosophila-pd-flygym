# Execution Guide

Render reports for one experiment definition:

```bash
python scripts/run_v2_experiment_report.py \
  --experiment configs/v2/experiments/healthy_baseline.json \
  --output-dir outputs/v2/experiment_reports/healthy_baseline \
  --dashboard outputs/v2/experiment_reports/healthy_baseline/dashboard.json
```

This command validates definitions and writes Markdown, HTML, and JSON reports.
It does not run FlyGym or MuJoCo.

Simulation execution should happen through the production campaign layer in a
FlyGym-enabled runtime.
