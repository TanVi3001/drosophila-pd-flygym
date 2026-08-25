"""Tests for read-only artifact inspection; no simulation is executed."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from drosophila_pd.artifact_analyzer import analyze_artifacts


def _write_dataset(root: Path, name: str, *, duplicate_source: Path | None = None) -> Path:
    dataset = root / "datasets" / "healthy" / name
    dataset.mkdir(parents=True)
    frames = [
        {"time": 0.0, "thorax": [0.0, 0.0, 1.0], "orientation": [1.0, 0.0, 0.0, 0.0]},
        {"time": 0.1, "thorax": [1.0, 0.0, 1.0], "orientation": [1.0, 0.0, 0.0, 0.0]},
        {"time": 0.2, "thorax": [2.0, 0.0, 1.0], "orientation": [1.0, 0.0, 0.0, 0.0]},
    ]
    rollout = {"metadata": {"dataset_id": name, "timestep_s": 0.1, "frame_count": 3, "duration_s": 0.2}, "frames": frames}
    rollout_path = dataset / "rollout.json"
    if duplicate_source is None:
        rollout_path.write_text(json.dumps(rollout), encoding="utf-8")
    else:
        rollout_path.write_bytes(duplicate_source.read_bytes())
    np.savez(dataset / "rollout.npz", time_s=np.array([0.0, 0.1, 0.2]), thorax_positions=np.array([[0, 0, 1], [1, 0, 1], [2, 0, 1]], dtype=float), thorax_quaternions=np.tile([1.0, 0.0, 0.0, 0.0], (3, 1)))
    (dataset / "metadata.json").write_text(json.dumps(rollout["metadata"]), encoding="utf-8")
    (dataset / "viewer_pose.json").write_text("{}", encoding="utf-8")
    files = {}
    for path in (dataset / "rollout.json", dataset / "rollout.npz", dataset / "metadata.json", dataset / "viewer_pose.json"):
        files[path.name] = {"path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    (dataset / "manifest.json").write_text(json.dumps({"frame_count": 3, "files": files}), encoding="utf-8")
    (dataset / "metrics.json").write_text(json.dumps({"scalar_metrics": {"walking_speed_mm_s": 10.0, "trajectory_efficiency": 1.0}}), encoding="utf-8")
    return rollout_path


def test_missing_dataset_writes_waiting_report(tmp_path):
    result = analyze_artifacts(repo_root=tmp_path, check_runtime=False)
    assert result.summary["status"] == "WAITING_DATASET"
    assert set(result.files) == {
        "artifact_summary.md", "artifact_summary.json", "integrity_report.csv", "dataset_report.csv",
        "metric_report.csv", "campaign_report.csv", "calibration_readiness.csv", "validation_readiness.csv",
    }


def test_dataset_integrity_and_metric_report(tmp_path):
    _write_dataset(tmp_path, "Healthy_001")
    result = analyze_artifacts(repo_root=tmp_path, check_runtime=False)
    assert result.summary["status"] == "WAITING_TARGET_DATA"
    assert result.summary["datasets"]["valid_count"] == 1
    metric_report = (result.output_dir / "metric_report.csv").read_text(encoding="utf-8")
    assert "walking_speed_mm_s" in metric_report
    assert "PASS" in metric_report
    assert "path_length_mm,UNAVAILABLE_METRIC" in metric_report


def test_duplicate_rollout_is_reported(tmp_path):
    first = _write_dataset(tmp_path, "Healthy_001")
    _write_dataset(tmp_path, "Healthy_002", duplicate_source=first)
    result = analyze_artifacts(repo_root=tmp_path, check_runtime=False)
    integrity = (result.output_dir / "integrity_report.csv").read_text(encoding="utf-8")
    assert "duplicate_rollout" in integrity
    assert "DUPLICATE" in integrity


def test_campaign_counts_are_reported(tmp_path):
    _write_dataset(tmp_path, "Healthy_001")
    campaign = tmp_path / "results" / "experimental_campaign"
    campaign.mkdir(parents=True)
    (campaign / "campaign_data.json").write_text(json.dumps({"conditions": [{"status": "COMPLETED"}, {"status": "FAILED"}, {"status": "WAITING_DATASET"}, {"status": "SKIPPED"}]}), encoding="utf-8")
    result = analyze_artifacts(repo_root=tmp_path, check_runtime=False)
    assert result.summary["campaign"]["completed"] == 1
    assert result.summary["campaign"]["failed"] == 1
    assert result.summary["campaign"]["waiting"] == 1
    assert result.summary["campaign"]["skipped"] == 1
