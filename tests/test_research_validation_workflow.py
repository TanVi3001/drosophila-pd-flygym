"""Regression tests for the read-only research validation workflow."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_research_workflow.py"
SPEC = importlib.util.spec_from_file_location("research_validation_workflow", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def _write_dataset(root: Path, name: str, *, offset: float = 0.0, bad_hash: bool = False) -> Path:
    dataset = root / name
    (dataset / "metrics").mkdir(parents=True)
    (dataset / "report").mkdir()
    (dataset / "figures").mkdir()
    frames = [
        {
            "timestamp_s": float(index) * 0.1,
            "thorax": [offset + float(index), 0.0, 1.0],
            "orientation": [1.0, 0.0, 0.0, 0.0],
            "com": [offset + float(index), 0.0, 1.0],
        }
        for index in range(3)
    ]
    (dataset / "rollout.json").write_text(json.dumps({"frames": frames}), encoding="utf-8")
    np.savez(dataset / "rollout.npz", thorax=np.asarray([[offset + i, 0.0, 1.0] for i in range(3)], dtype=float))
    metrics = {
        "dataset_id": name,
        "frame_count": 3,
        "duration_s": 0.2,
        "timestep_s": 0.1,
        "walking_speed_mm_s": 10.0 + offset,
        "walking_speed_max_mm_s": 12.0 + offset,
        "total_distance_mm": 2.0 + offset,
        "heading_variance_rad2": 0.0,
        "body_orientation_variance_rad2": 0.0,
        "symmetry_index": 1.0,
        "trajectory_curvature_mean_rad_per_mm": 0.0,
    }
    (dataset / "metrics" / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
    (dataset / "metrics" / "metrics.csv").write_text("metric,value\nframe_count,3\n", encoding="utf-8")
    (dataset / "report" / "summary.md").write_text("# Summary\n", encoding="utf-8")
    (dataset / "report" / "dashboard.html").write_text("<!doctype html>", encoding="utf-8")
    (dataset / "figures" / "speed.png").write_bytes(b"fixture")
    pose = {"frame_count": 3, "frames": [{"frame_index": i, "orientation": [1.0, 0.0, 0.0, 0.0]} for i in range(3)]}
    (dataset / "viewer_pose.json").write_text(json.dumps(pose), encoding="utf-8")
    (dataset / "metadata.json").write_text(json.dumps({"dataset_id": name, "timestep_s": 0.1}), encoding="utf-8")

    files = {}
    for path in sorted(dataset.iterdir()):
        if path.is_file():
            files[path.name] = {"path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    manifest = {"frame_count": 3, "files": files, "schema_version": "1.0"}
    if bad_hash:
        manifest["files"]["rollout.json"]["sha256"] = "0" * 64
    (dataset / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return dataset


def test_missing_dataset_is_waiting_without_payload_creation(tmp_path: Path) -> None:
    output = tmp_path / "validation"
    result = MODULE.validate_dataset(tmp_path / "missing", output=output)

    assert result["status"] == "WAITING_DATASET"
    assert not (tmp_path / "missing" / "rollout.json").exists()
    assert (output / "validation_report.md").is_file()


def test_dataset_validation_checks_frames_quaternions_com_and_metrics(tmp_path: Path) -> None:
    dataset = _write_dataset(tmp_path, "Healthy_001")
    result = MODULE.validate_dataset(dataset, output=tmp_path / "validation")

    assert result["status"] == "PASS"
    assert result["checks"]["frame_count"]["sources"]["rollout.json"] == 3
    assert result["checks"]["quaternion"]["pass"] is True
    assert result["checks"]["com"]["pass"] is True
    assert (tmp_path / "validation" / "validation_report.md").is_file()


def test_integrity_reports_hash_mismatch(tmp_path: Path) -> None:
    dataset = _write_dataset(tmp_path, "Broken", bad_hash=True)
    result = MODULE.verify_artifact_integrity(dataset, output=tmp_path / "validation")

    assert result["status"] == "INVALID_ARTIFACTS"
    assert any(item["code"] == "HASH_MISMATCH" for item in result["issues"])
    assert (tmp_path / "validation" / "integrity_report.md").is_file()


def test_integrity_rejects_manifest_paths_outside_dataset_root(tmp_path: Path) -> None:
    dataset = _write_dataset(tmp_path, "Traversal")
    outside = tmp_path / "outside.txt"
    outside.write_text("must not be read", encoding="utf-8")
    manifest_path = dataset / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"]["outside"] = {
        "path": "../outside.txt",
        "sha256": hashlib.sha256(outside.read_bytes()).hexdigest(),
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = MODULE.verify_artifact_integrity(dataset, output=tmp_path / "validation")

    assert result["status"] == "INVALID_ARTIFACTS"
    assert any(item["code"] == "MANIFEST_PATH_UNSAFE" for item in result["issues"])


def test_cross_run_reports_numeric_differences_only(tmp_path: Path) -> None:
    first = _write_dataset(tmp_path, "Healthy_001")
    second = _write_dataset(tmp_path, "Healthy_002", offset=2.0)
    result = MODULE.compare_rollouts([first, second], output=tmp_path / "validation")

    assert any(row["metric"] == "walking_speed_mm_s" for row in result["differences"])
    assert all(set(row) == {"metric", "values", "difference", "available_count"} for row in result["differences"])
    assert (tmp_path / "validation" / "cross_run_consistency.md").is_file()


def test_boundary_scan_distinguishes_disclaimer_and_potential_overclaim(tmp_path: Path) -> None:
    (tmp_path / "safe.md").write_text("This is not a diagnosis and does not provide clinical prediction.\n", encoding="utf-8")
    (tmp_path / "review.md").write_text("This tool provides clinical prediction.\n", encoding="utf-8")

    result = MODULE.check_scientific_boundaries(tmp_path, output=tmp_path / "validation")

    assert result["status"] == "REVIEW_REQUIRED"
    assert any(item["classification"] == "boundary_disclaimer" for item in result["findings"])
    assert any(item["classification"] == "potential_overclaim" for item in result["findings"])
