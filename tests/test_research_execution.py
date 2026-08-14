"""Contract tests for the dataset-gated V6 execution layer."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

from drosophila_pd.research_execution import (
    ArtifactRegistry,
    DatasetDiscovery,
    ExecutionContext,
    ExecutionHistory,
    ExecutionRuntime,
    ExecutionState,
)


def test_execution_state_machine_rejects_skipped_transitions() -> None:
    history = ExecutionHistory()
    history.transition(ExecutionState.READY)
    history.transition(ExecutionState.RUNNING)
    history.transition(ExecutionState.VALIDATING)
    history.transition(ExecutionState.EXPORTING)
    history.transition(ExecutionState.COMPLETED)
    assert history.state is ExecutionState.COMPLETED
    with pytest.raises(ValueError, match="invalid execution transition"):
        history.transition(ExecutionState.RUNNING)


def test_dataset_discovery_ignores_planning_template_and_does_not_parse_rollout(tmp_path: Path) -> None:
    planning = tmp_path / "research" / "campaigns" / "healthy_baseline"
    planning.mkdir(parents=True)
    (planning / "dataset_manifest.template.json").write_text(
        json.dumps({"status": "PLANNING_ONLY", "entries": []}), encoding="utf-8"
    )
    result = DatasetDiscovery().discover((tmp_path / "datasets", tmp_path / "research" / "datasets"))
    assert result.state is ExecutionState.WAITING_DATASET
    assert result.datasets == []
    assert result.as_dict()["rollout_parsing"] == "not performed"


def test_manifest_without_payload_is_waiting(tmp_path: Path) -> None:
    root = tmp_path / "datasets" / "healthy"
    root.mkdir(parents=True)
    (root / "manifest.json").write_text(
        json.dumps({"dataset_id": "healthy", "status": "READY", "entries": []}), encoding="utf-8"
    )
    result = DatasetDiscovery().discover((tmp_path / "datasets",))
    assert result.state is ExecutionState.WAITING_DATASET
    assert result.datasets[0].reason == "Manifest contains no payload entries."


def test_artifact_registry_registers_existing_files_and_verifies(tmp_path: Path) -> None:
    report = tmp_path / "reports" / "report.json"
    report.parent.mkdir()
    report.write_text("{}\n", encoding="utf-8")
    registry = ArtifactRegistry(tmp_path)
    record = registry.register(report, "reports")
    assert record.byte_size > 0
    assert registry.verify()["overall_pass"] is True
    with pytest.raises(FileNotFoundError):
        registry.register(tmp_path / "missing.json", "reports")
    with pytest.raises(ValueError, match="unsupported artifact category"):
        registry.register(report, "unknown")


def test_execute_waits_without_calling_downstream_pipeline(tmp_path: Path) -> None:
    called = False

    def fail_if_called(*_args: object) -> None:
        nonlocal called
        called = True
        raise AssertionError("downstream pipeline must not run without a dataset")

    context = ExecutionContext(tmp_path, output_root=tmp_path / "execution")
    result = ExecutionRuntime(context, study_runner=fail_if_called).execute()
    assert result.state is ExecutionState.WAITING_DATASET
    assert called is False
    assert (tmp_path / "execution" / "execution_report.json").is_file()
    assert (tmp_path / "execution" / "execution_report.md").is_file()
    payload = json.loads((tmp_path / "execution" / "execution_report.json").read_text(encoding="utf-8"))
    assert payload["state"] == "WAITING_DATASET"
    assert all(item["status"] == "WAITING_DATASET" for item in payload["stages"])


def test_cli_discover_reports_waiting_dataset(tmp_path: Path) -> None:
    script = Path(__file__).resolve().parents[1] / "scripts" / "run_campaign.py"
    completed = subprocess.run(
        [sys.executable, str(script), "discover", "--root", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["state"] == "WAITING_DATASET"
    assert payload["rollout_parsing"] == "not performed"
