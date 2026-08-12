# Tutorial

Build a dataset from completed campaign outputs:

```bash
python scripts/build_v2_dataset.py \
  --dataset-id v2_campaign_dataset \
  --source-root outputs/v2/scientific_campaign \
  --output-dir outputs/v2/datasets \
  --force
```

Build a documentation-only synthetic demo dataset:

```bash
python scripts/build_v2_dataset.py \
  --dataset-id synthetic_dataset_factory_demo \
  --output-dir outputs/v2/datasets \
  --synthetic-demo
```

Request additional formats:

```bash
python scripts/build_v2_dataset.py \
  --dataset-id v2_campaign_dataset \
  --source-root outputs/v2/scientific_campaign \
  --output-dir outputs/v2/datasets \
  --format json \
  --format csv \
  --format npz
```

Optional Parquet, Arrow, and HDF5 exports require their optional Python
dependencies.
