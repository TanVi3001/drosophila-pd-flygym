# Limitations

- Local runtimes without FlyGym can validate campaign plumbing but cannot
  produce simulation rollouts.
- The production layer delegates simulation to existing canonical code and does
  not alter controllers or perturbations.
- UMAP and t-SNE are dependency-free compatible embeddings unless future
  optional backends are explicitly added.
- Campaign labels are computational labels.
- Figure generation depends on available rollout arrays and metrics.
- Biological validation remains future work.
