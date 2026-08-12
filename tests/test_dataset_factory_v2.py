from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from drosophila_pd.behavior_platform import (  # noqa: E402
    DATASET_EXPORT_FORMATS,
    DATASET_FACTORY_SCOPE,
    DatasetFactory,
    DatasetFactoryConfig,
    coverage_report,
    dataset_statistics,
    deduplicate_dataset,
    export_dataset,
    incremental_update_dataset,
    load_dataset,
    merge_datasets,
    missing_data_report,
    quality_report,
    render_dataset_card,
    split_dataset,
    synthetic_demo_dataset,
    validate_dataset_factory_output,
    write_dataset_reports,
)
from drosophila_pd.behavior_platform.ai_dataset import DatasetLoader, create_dataset_manifest


def _write_result(path: Path, *, experiment_id: str, condition: str, seed: int, duplicate: bool = False) -> None:
    payload = {
        "sample_id": experiment_id if duplicate else f"{experiment_id}_{seed}",
        "condition": condition,
        "experiment": {
            "experiment_id": experiment_id if duplicate else f"{experiment_id}_{seed}",
            "campaign_id": "campaign_a",
            "role": condition,
            "seed": seed,
            "replicate": 0,
        },
        "arrays": {
            "thorax_positions": [[0.0, 0.0, 1.0], [1.0 + seed, 0.1, 1.0], [2.0 + seed, 0.2, 1.0]],
            "heading": [0.0, 0.1, 0.2],
        },
        "metrics": {"mean_speed": 1.0 + seed, "yaw_rate_abs_mean": 0.1},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_dataset_factory_discovery_build_cache_and_reports(tmp_path):
    campaign_root = tmp_path / "campaigns"
    _write_result(campaign_root / "campaign_a" / "reports" / "rollout_0.json", experiment_id="exp_a", condition="Healthy", seed=0)
    _write_result(campaign_root / "campaign_a" / "reports" / "rollout_1.json", experiment_id="exp_b", condition="Candidate", seed=1)
    (campaign_root / "campaign_a" / "reports" / "dataset_manifest.json").write_text("{}", encoding="utf-8")
    config = DatasetFactoryConfig(
        dataset_id="factory_dataset",
        source_roots=(campaign_root.as_posix(),),
        output_dir=(tmp_path / "datasets").as_posix(),
        export_formats=("json", "csv", "npz"),
    )
    factory = DatasetFactory(config)
    assert factory.discover_campaigns() == (campaign_root,)
    index = factory.index_rollouts()
    assert len(index) == 2
    assert all(entry.has_arrays and entry.has_metrics for entry in index)
    dataset = factory.assemble_dataset()
    assert len(dataset.samples) == 2
    result = factory.build()
    assert result.cache_hit is False
    assert result.validation["overall_pass"] is True
    assert Path(result.manifest_path).exists()
    assert "card" in result.reports
    second = factory.build()
    assert second.cache_hit is True
    loaded = DatasetLoader.load(result.files["json"])
    assert loaded.dataset_id == "factory_dataset"


def test_dataset_splits_merge_incremental_deduplicate_and_quality(tmp_path):
    dataset = synthetic_demo_dataset()
    assert dataset.metadata["synthetic"] is True
    duplicate = type(dataset)(
        dataset_id=dataset.dataset_id,
        version=dataset.version,
        samples=dataset.samples + (dataset.samples[0],),
        metadata=dataset.metadata,
    )
    deduped = deduplicate_dataset(duplicate)
    assert len(deduped.samples) == len(dataset.samples)
    splits = split_dataset(dataset, {"train": 0.5, "validation": 0.25, "test": 0.25})
    assert sum(len(values) for values in splits.values()) == len(dataset.samples)
    merged = merge_datasets([dataset, synthetic_demo_dataset(dataset_id="other")], dataset_id="merged", version="v2")
    assert len(merged.samples) == 12
    updated = incremental_update_dataset(dataset, duplicate)
    assert len(updated.samples) == len(dataset.samples)
    stats = dataset_statistics(dataset)
    assert stats["features_finite"] is True
    assert coverage_report(dataset)["sample_count"] == len(dataset.samples)
    assert quality_report(dataset)["overall_pass"] is True
    assert missing_data_report(dataset)["overall_pass"] is True
    card = render_dataset_card(dataset)
    assert "Dataset Card" in card
    assert "Scientific Scope" in card
    with pytest.raises(ValueError, match="split ratios"):
        split_dataset(dataset, {})


def test_dataset_exports_optional_formats_and_validation(tmp_path):
    dataset = synthetic_demo_dataset()
    files = export_dataset(dataset, tmp_path, formats=("json", "csv", "npz"))
    assert all(path.exists() and path.stat().st_size > 0 for path in files.values())
    assert load_dataset(files["json"]).dataset_id == dataset.dataset_id
    assert load_dataset(files["npz"]).samples[0].sample_id == dataset.samples[0].sample_id
    reports = write_dataset_reports(dataset, output_dir=tmp_path / "reports", split_ratios={"train": 1.0})
    assert all(path.exists() for path in reports.values())
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(create_dataset_manifest(dataset).as_dict()), encoding="utf-8")
    validation = validate_dataset_factory_output(dataset, manifest_path=manifest_path, files=files)
    assert validation["overall_pass"] is True
    for fmt in ("parquet", "arrow", "hdf5"):
        try:
            optional = export_dataset(dataset, tmp_path / fmt, formats=(fmt,))
            assert optional[fmt].exists()
        except RuntimeError as exc:
            assert "required" in str(exc)
    assert set(DATASET_EXPORT_FORMATS) == {"json", "csv", "npz", "parquet", "arrow", "hdf5"}


def test_metric_only_campaign_result_and_validation_errors(tmp_path):
    source = tmp_path / "source"
    result_path = source / "campaign" / "reports" / "metrics_only.json"
    result_path.parent.mkdir(parents=True)
    result_path.write_text(
        json.dumps(
            {
                "condition": "Summary",
                "experiment": {"experiment_id": "metrics_only", "campaign_id": "campaign", "role": "Summary", "seed": 0},
                "metrics": {"mean_speed": 1.0, "path_length": 2.0},
            }
        ),
        encoding="utf-8",
    )
    factory = DatasetFactory(
        DatasetFactoryConfig(
            dataset_id="metric_only",
            source_roots=(source.as_posix(),),
            output_dir=(tmp_path / "out").as_posix(),
        )
    )
    report = factory.build(force=True)
    assert report.validation["overall_pass"] is True
    stats = json.loads(Path(report.reports["statistics"]).read_text(encoding="utf-8"))
    assert "mean_speed" in stats["feature_names"]
    with pytest.raises(ValueError, match="dataset_id"):
        DatasetFactory(DatasetFactoryConfig(dataset_id=""))
    with pytest.raises(ValueError, match="unsupported"):
        DatasetFactory(DatasetFactoryConfig(dataset_id="bad", export_formats=("bad",)))


def test_dataset_factory_cli_synthetic_demo(tmp_path):
    script = REPO_ROOT / "scripts" / "build_v2_dataset.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--dataset-id",
            "synthetic_cli_demo",
            "--output-dir",
            str(tmp_path),
            "--synthetic-demo",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["overall_pass"] is True
    assert payload["synthetic"] is True
    assert Path(payload["reports"]["card"]).exists()
    card = Path(payload["reports"]["card"]).read_text(encoding="utf-8")
    assert DATASET_FACTORY_SCOPE in card
