# Developer Guide

Keep Dataset Factory changes production-oriented and additive.

Do:

- reuse `BehaviorDataset` and `CampaignDatasetBuilder`;
- keep synthetic demo data clearly labeled;
- preserve deterministic splitting and hashing;
- validate manifests and exported files;
- support metric-only campaign summaries as well as rollout arrays.

Do not:

- run simulations from the factory;
- alter FlyGym controllers;
- rewrite frozen evidence;
- infer biological meaning from dataset summaries;
- treat synthetic demo data as scientific evidence.
