# Architecture

The production layer has five responsibilities.

1. Campaign library loading verifies each stored `CampaignConfig` hash.
2. Batch execution delegates to the existing `CampaignRunner` and uses
   `FlyGymBatchExecutor` only when FlyGym is available.
3. Dataset production creates the canonical output folders:
   `rollouts`, `measurements`, `behavior`, `gait`, `open_field`,
   `digital_twin`, `reports`, `figures`, `videos`, and `metadata`.
4. Automatic analysis reuses the AI platform for feature matrices,
   descriptive statistics, PCA, t-SNE-compatible embeddings,
   UMAP-compatible embeddings, clustering, benchmark summaries, and similarity
   matrices.
5. Validation checks folder completeness, manifests, hashes, provenance, and
   dataset integrity.

No production-campaign function imports FlyGym as part of analysis. FlyGym is
checked lazily at execution time.
