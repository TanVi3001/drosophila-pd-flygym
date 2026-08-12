# Dataset Guide

Canonical production datasets use this folder structure:

- `rollouts/`
- `measurements/`
- `behavior/`
- `gait/`
- `open_field/`
- `digital_twin/`
- `reports/`
- `figures/`
- `videos/`
- `metadata/`

`build_scientific_dataset_package` exports dataset JSON, CSV, NPZ, manifest,
index, and artifact manifest files under the campaign metadata directory.

Every artifact should be traceable through a manifest, checksum, campaign ID,
configuration hash, seed, and provenance record.
