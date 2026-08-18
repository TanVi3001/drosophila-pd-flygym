"""Regression tests for sequential imported-rollout experiment management."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from drosophila_pd.experiment_manager import ExperimentManager


def _write_rollout(root: Path, name: str, offset: float = 0.0) -> Path:
    dataset = root / "datasets" / "healthy" / name
    dataset.mkdir(parents=True)
    frames = []
    for index in range(4):
        frames.append({
            "timestamp_s": index * 0.5,
            "thorax": [offset + index, 0.0, 1.0],
            "com": [offset + index, 0.0, 1.1],
            "orientation": [1.0, 0.0, 0.0, 0.0],
            "joint_velocity": {"joint_a": float(index)},
            "joint_acceleration": {"joint_a": 1.0},
            "contact": {"LF": int(index % 2 == 0), "RF": int(index % 2 == 1)},
        })
    (dataset / "rollout.json").write_text(json.dumps({"metadata": {"timestep_s": 0.5}, "frames": frames}), encoding="utf-8")
    return dataset


def _write_config(root: Path, identifier: str, dataset: str) -> None:
    config_dir = root / "experiments"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / f"{identifier}.yaml").write_text(
        f"experiment_id: {identifier}\nname: {identifier}\ncondition: healthy\ndataset: {dataset}\nseed: 4\n",
        encoding="utf-8",
    )


def test_manager_runs_multiple_configs_and_writes_comparison_package(tmp_path: Path) -> None:
    _write_rollout(tmp_path, "Healthy_001")
    _write_rollout(tmp_path, "Healthy_002", offset=2.0)
    _write_config(tmp_path, "healthy_a", "datasets/healthy/Healthy_001")
    _write_config(tmp_path, "healthy_b", "datasets/healthy/Healthy_002")

    summary = ExperimentManager(tmp_path, output_root="results/suite", config_dir="experiments").run()

    assert summary["counts"]["COMPLETED"] == 2
    assert summary["counts"]["WAITING_DATASET"] == 0
    for identifier in ("healthy_a", "healthy_b"):
        root = tmp_path / "results" / "suite" / identifier
        assert (root / "rollout" / "rollout.json").is_file()
        assert (root / "metrics" / "metrics.json").is_file()
        assert (root / "report" / "summary.md").is_file()
        assert all((root / "figures" / f"{name}.png").is_file() for name in ("speed", "trajectory", "orientation"))
    comparison = tmp_path / "results" / "suite" / "comparison"
    assert all((comparison / f"{name}.png").is_file() for name in (
        "boxplot", "violin_plot", "histogram", "trajectory_overlay", "com_comparison",
        "speed_comparison", "orientation_comparison", "joint_comparison",
    ))
    assert (tmp_path / "results" / "suite" / "experiment_summary.csv").is_file()
    assert (tmp_path / "results" / "suite" / "final_report.html").read_text(encoding="utf-8").find("Plotly") >= 0


def test_manager_reports_missing_dataset_without_fabricating_outputs(tmp_path: Path) -> None:
    (tmp_path / "datasets" / "healthy" / "Missing").mkdir(parents=True)
    _write_config(tmp_path, "waiting", "datasets/healthy/Missing")

    summary = ExperimentManager(tmp_path, output_root="results/suite").run()

    assert summary["counts"]["WAITING_DATASET"] == 1
    root = tmp_path / "results" / "suite" / "waiting"
    record = json.loads((root / "experiment.json").read_text(encoding="utf-8"))
    assert record["status"] == "WAITING_DATASET"
    assert not (root / "metrics" / "metrics.json").exists()
    assert (root / "report" / "summary.md").is_file()


def test_manager_resume_keeps_completed_record(tmp_path: Path) -> None:
    _write_rollout(tmp_path, "Healthy_001")
    _write_config(tmp_path, "healthy", "datasets/healthy/Healthy_001")
    manager = ExperimentManager(tmp_path, output_root="results/suite")
    first = manager.run()
    record_path = tmp_path / "results" / "suite" / "healthy" / "experiment.json"
    before = record_path.read_text(encoding="utf-8")
    second = manager.run()

    assert first["counts"] == second["counts"]
    assert record_path.read_text(encoding="utf-8") == before
