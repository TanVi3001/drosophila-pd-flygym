# Architecture

The Dataset Factory pipeline:

1. Discover completed campaign folders.
2. Index rollout and report JSON files.
3. Assemble `BehaviorDataset` samples.
4. Deduplicate samples by ID and checksum.
5. Export JSON, CSV, NPZ, optional Parquet, optional Arrow, and optional HDF5.
6. Write dataset manifests and checksums.
7. Generate deterministic train, validation, and test partitions.
8. Generate statistics, metadata, feature, coverage, quality, missing-data, and
   dataset-card reports.
9. Validate dataset consistency and artifact integrity.

Caching uses the discovered input index hash. Incremental updates merge new
samples into an existing dataset and deduplicate the result.
