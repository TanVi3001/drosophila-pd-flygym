"""Regression tests for the read-only rollout analysis pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from drosophila_pd.analysis import analyze_rollout, compute_metrics, load_rollout


def test_analysis_pipeline_reads_json_and_writes_complete_package(tmp_path: Path) -> None:
    dataset = tmp_path / "Healthy_001"
    dataset.mkdir()
    frames = []
    for index, yaw in enumerate((0.0, 0.1, 0.2, 0.2, 0.3)):
        frames.append(
            {
                "timestamp_s": float(index),
                "thorax": [float(index), float(index > 2), 1.0],
                "com": [float(index), float(index > 2), 1.1],
                "orientation": [np.cos(yaw / 2), 0.0, 0.0, np.sin(yaw / 2)],
                "joint_velocity": {"joint_a": float(index)},
                "joint_acceleration": {"joint_a": 1.0},
                "contact": {"LF": int(index % 2 == 0), "RF": int(index % 2 == 1)},
            }
        )
    (dataset / "rollout.json").write_text(
        json.dumps(
            {
                "schema_version": "flygym-rollout-1",
                "metadata": {"dataset_id": "Healthy_001", "timestep_s": 1.0, "quaternion_order": "wxyz"},
                "frames": frames,
            }
        ),
        encoding="utf-8",
    )

    result = analyze_rollout(dataset, tmp_path / "results")

    assert result.metrics["frame_count"] == 5
    assert result.metrics["total_distance_mm"] == 3.0 + np.sqrt(2.0)
    assert result.metrics["walking_speed_mm_s"] > 0
    assert result.metrics["com_velocity_mean_mm_s"] is not None
    assert result.metrics["joint_rms_velocity"]["joint_a"] > 0
    assert result.metrics["contact_available"] is True
    assert result.metrics["symmetry_index"] == 0.8
    assert set(result.files) >= {
        "metrics_json",
        "metrics_csv",
        "summary",
        "dashboard",
        *(f"figure_{name}" for name in ("speed", "trajectory", "orientation", "joint_velocity", "joint_acceleration", "contact_ratio", "comparison")),
    }
    assert all(path.is_file() and path.stat().st_size > 0 for path in result.files.values())
    payload = json.loads(result.files["metrics_json"].read_text(encoding="utf-8"))
    assert payload["scientific_scope"].startswith("Computational metrics")


def test_analysis_pipeline_reads_rollout_arrays_npz_without_json(tmp_path: Path) -> None:
    dataset = tmp_path / "Healthy_002"
    dataset.mkdir()
    positions = np.asarray([[0.0, 0.0, 1.0], [2.0, 0.0, 1.0], [3.0, 1.0, 1.0]])
    quaternions = np.asarray([[1.0, 0.0, 0.0, 0.0]] * 3)
    np.savez(
        dataset / "rollout_arrays.npz",
        time_s=np.asarray([0.0, 0.5, 1.0]),
        thorax_positions=positions,
        thorax_quaternions=quaternions,
        com_positions=positions + [0.0, 0.0, 0.1],
        joint__joint_a=np.asarray([0.0, 0.2, 0.8]),
        contact__LF=np.asarray([1.0, 0.0, 1.0]),
        contact__RF=np.asarray([1.0, 1.0, 0.0]),
    )
    (dataset / "metadata.json").write_text(
        json.dumps({"dataset_id": "Healthy_002", "timestep_s": 0.5, "quaternion_order": "wxyz"}),
        encoding="utf-8",
    )

    loaded = load_rollout(dataset)
    metrics = compute_metrics(loaded)

    assert loaded.source_files[0].name == "rollout_arrays.npz"
    assert loaded.frame_count == 3
    assert metrics["total_distance_mm"] == 2.0 + np.sqrt(2.0)
    assert metrics["stride_frequency_hz"] is not None
    assert metrics["joint_rms_acceleration"]["joint_a"] > 0


def test_missing_optional_channels_are_reported_without_fake_values(tmp_path: Path) -> None:
    dataset = tmp_path / "minimal"
    dataset.mkdir()
    (dataset / "rollout.json").write_text(
        json.dumps(
            {
                "metadata": {"timestep_s": 0.25},
                "frames": [
                    {"timestamp_s": 0.0, "thorax": [0.0, 0.0, 1.0]},
                    {"timestamp_s": 0.25, "thorax": [1.0, 0.0, 1.0]},
                ],
            }
        ),
        encoding="utf-8",
    )

    result = analyze_rollout(dataset, tmp_path / "minimal-results")

    assert result.metrics["available_channels"]["com"] is False
    assert result.metrics["com_trajectory"] is None
    assert result.metrics["stride_frequency_hz"] is None
    assert result.metrics["contact_ratio"] == {}
    assert result.files["figure_contact_ratio"].is_file()
