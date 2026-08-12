# Dataset Guide

Factory output includes:

- dataset exports;
- `dataset_manifest.json`;
- `dataset_statistics.json`;
- `dataset_metadata.json`;
- `feature_summary.json`;
- `coverage_report.json`;
- `quality_report.json`;
- `missing_data_report.json`;
- `dataset_splits.json`;
- `README.md` dataset card;
- `dataset_factory_cache.json`.

Default partitions are deterministic train, validation, and test splits using
sample IDs and stable hashing.

Dataset merging and incremental updates deduplicate by sample ID and full sample
checksum.
