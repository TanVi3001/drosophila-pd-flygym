# Execution Guide

Create or resume a production campaign in a FlyGym-enabled runtime:

```bash
python scripts/run_scientific_production_campaign.py \
  --campaign configs/v2/campaigns/healthy_baseline.json \
  --output-root outputs/v2/scientific_campaign
```

For local infrastructure checks without FlyGym:

```bash
python scripts/run_scientific_production_campaign.py \
  --campaign configs/v2/campaigns/healthy_baseline.json \
  --output-root outputs/v2/scientific_campaign \
  --max-experiments 1 \
  --allow-deferred-without-flygym
```

If FlyGym is unavailable, simulation execution is not attempted. The campaign
engine records deferred execution status instead.

Checkpoint recovery uses `metadata/campaign_checkpoint.json`.
