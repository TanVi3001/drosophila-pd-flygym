"""Regression tests for the gated one-command research orchestrator."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_research_pipeline.py"
SPEC = importlib.util.spec_from_file_location("run_research_pipeline", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _runtime_ready(_root: Path) -> dict[str, object]:
    return {"overall_pass": True, "readiness": {"runtime": True}}


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
    dataset = tmp_path / "datasets" / "healthy" / "Healthy_001"
    dataset.mkdir(parents=True)
    (dataset / "rollout.json").write_text(json.dumps({"frames": [{"timestamp_s": 0.0}]}), encoding="utf-8")
    (dataset / "rollout.npz").write_bytes(b"test fixture marker")

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
