# V2 Dataset Factory

The Dataset Factory is the production layer that transforms completed Version 2
simulation campaigns into reusable computational datasets.

It reuses existing v2 components:

- `BehaviorDataset`, `BehaviorSample`, manifests, and exporters;
- `CampaignDatasetBuilder`;
- feature extraction;
- checksum and provenance helpers;
- synthetic examples for documentation-only demos.

The factory does not run FlyGym, alter controllers, introduce perturbations, or
create biological claims.
