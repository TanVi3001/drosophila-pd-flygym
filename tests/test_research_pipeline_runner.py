"""Regression tests for the gated one-command research orchestrator."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_research_pipeline.py"
SPEC = importlib.util.spec_from_file_location("run_research_pipeline", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _runtime_ready(_root: Path) -> dict[str, object]:
    return {"overall_pass": True, "readiness": {"runtime": True}}


def _write_valid_dataset(root: Path, name: str = "Healthy_001") -> Path:
    dataset = root / "datasets" / "healthy" / name
    (dataset / "metrics").mkdir(parents=True)
    (dataset / "rollout.json").write_text(
        json.dumps(
            {
                "frames": [
                    {
                        "timestamp_s": 0.0,
                        "thorax": [0.0, 0.0, 0.0],
                        "orientation": [1.0, 0.0, 0.0, 0.0],
                        "com": [0.0, 0.0, 0.0],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    np.savez(dataset / "rollout.npz", thorax=np.zeros((1, 3), dtype=float))
    (dataset / "viewer_pose.json").write_text(
        json.dumps({"frame_count": 1, "frames": [{"frame_index": 0, "orientation": [1.0, 0.0, 0.0, 0.0]}]}),
        encoding="utf-8",
    )
    (dataset / "metadata.json").write_text(json.dumps({"dataset_id": name}), encoding="utf-8")
    (dataset / "manifest.json").write_text(json.dumps({"schema_version": "1.0"}), encoding="utf-8")
    (dataset / "metrics" / "metrics.json").write_text(
        json.dumps(
            {
                "dataset_id": name,
                "frame_count": 1,
                "walking_speed_mm_s": 0.0,
                "total_distance_mm": 0.0,
                "heading_variance_rad2": 0.0,
                "body_orientation_variance_rad2": 0.0,
                "symmetry_index": 1.0,
                "trajectory_curvature_mean_rad_per_mm": 0.0,
            }
        ),
        encoding="utf-8",
    )
    return dataset


def test_runtime_unavailable_stops_before_dataset_generation(tmp_path: Path) -> None:
    called = []

    def dataset_generator(_root: Path) -> dict[str, object]:
        called.append("dataset")
        return {}

    result = MODULE.run_research_pipeline(
        tmp_path,
        runtime_checker=lambda _root: {"overall_pass": False, "python": "3.13.5"},
        dataset_generator=dataset_generator,
    )

    assert called == []
    assert result["statuses"]["runtime"]["status"] == "WAITING_RUNTIME"
    assert result["statuses"]["dataset"]["status"] == "WAITING_RUNTIME"
    assert result["statuses"]["experiment"]["status"] == "SKIPPED"
    assert (tmp_path / "results" / "research_status.json").is_file()


def test_dataset_gate_waits_without_real_rollout(tmp_path: Path) -> None:
    calls = []

    def experiment_runner(_root: Path) -> dict[str, object]:
        calls.append("experiment")
        return {"counts": {"COMPLETED": 1}}

    result = MODULE.run_research_pipeline(
        tmp_path,
        runtime_checker=_runtime_ready,
        dataset_generator=lambda _root: {"counts": {"FAILED": 0}},
        experiment_runner=experiment_runner,
    )

    assert calls == []
    assert result["statuses"]["dataset"]["status"] == "WAITING_DATASET"
    assert result["statuses"]["experiment"]["status"] == "SKIPPED"


def test_successful_orchestration_uses_hooks_without_simulation(tmp_path: Path) -> None:
    _write_valid_dataset(tmp_path)

    result = MODULE.run_research_pipeline(
        tmp_path,
        runtime_checker=_runtime_ready,
        dataset_generator=lambda _root: {"counts": {"FAILED": 0}},
        experiment_runner=lambda _root: {"counts": {"COMPLETED": 1, "FAILED": 0}},
        biomarker_runner=lambda _root: {"count": 1, "failed": {}},
        validation_runner=lambda _root: {"count": 1},
        release_runner=lambda _root: {"readiness": "READY"},
        publication_runner=lambda _root: {"status": "READY"},
    )

    assert all(result["statuses"][name]["status"] == "PASS" for name in MODULE.STAGE_NAMES)
    assert result["blockers"] == []
    assert (tmp_path / "results" / "progress_summary.md").is_file()
    assert (tmp_path / "results" / "final_execution_report.md").is_file()


def test_biomarker_failure_stops_validation_release_and_publication(tmp_path: Path) -> None:
    _write_valid_dataset(tmp_path)
    calls: list[str] = []

    def mark(name: str, value: dict[str, object]):
        def callback(_root: Path) -> dict[str, object]:
            calls.append(name)
            return value

        return callback

    result = MODULE.run_research_pipeline(
        tmp_path,
        runtime_checker=_runtime_ready,
        dataset_generator=lambda _root: {"counts": {"FAILED": 0}},
        experiment_runner=lambda _root: {"counts": {"COMPLETED": 1, "FAILED": 0}},
        biomarker_runner=mark("biomarkers", {"count": 0, "failed": {"Healthy_001": "broken"}}),
        validation_runner=mark("validation", {"count": 1}),
        release_runner=mark("release", {"readiness": "READY"}),
        publication_runner=mark("publication", {"status": "READY"}),
    )

    assert calls == ["biomarkers"]
    assert result["statuses"]["biomarkers"]["status"] == "FAILED"
    assert result["statuses"]["validation"]["status"] == "SKIPPED"
    assert result["statuses"]["release"]["status"] == "SKIPPED"
    assert result["statuses"]["publication"]["status"] == "SKIPPED"


def test_validation_failure_stops_release_and_publication(tmp_path: Path) -> None:
    _write_valid_dataset(tmp_path)
    calls: list[str] = []

    def release(_root: Path) -> dict[str, object]:
        calls.append("release")
        return {"readiness": "READY"}

    def publication(_root: Path) -> dict[str, object]:
        calls.append("publication")
        return {"status": "READY"}

    result = MODULE.run_research_pipeline(
        tmp_path,
        runtime_checker=_runtime_ready,
        dataset_generator=lambda _root: {"counts": {"FAILED": 0}},
        experiment_runner=lambda _root: {"counts": {"COMPLETED": 1, "FAILED": 0}},
        biomarker_runner=lambda _root: {"count": 1, "failed": {}},
        validation_runner=lambda _root: {
            "datasets": [
                {
                    "dataset_id": "Healthy_001",
                    "validation": {"overall_pass": False},
                    "integrity": {"overall_pass": False},
                }
            ]
        },
        release_runner=release,
        publication_runner=publication,
    )

    assert calls == []
    assert result["statuses"]["validation"]["status"] == "FAILED"
    assert result["statuses"]["release"]["status"] == "SKIPPED"
    assert result["statuses"]["publication"]["status"] == "SKIPPED"
