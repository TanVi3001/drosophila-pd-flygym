"""Tests for release audit outputs without simulation or fabricated data."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_release_audit.py"
SPEC = importlib.util.spec_from_file_location("build_release_audit", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_release_audit_waits_without_runtime_or_dataset(tmp_path: Path) -> None:
    (tmp_path / "datasets").mkdir()
    result = MODULE.build_release_audit(tmp_path)

    assert result["dataset_registry_status"] == "WAITING_DATASET"
    assert result["performance_status"] == "WAITING_RUNTIME"
    assert result["paper_status"] == "WAITING_DATASET"
    assert result["readiness"] == "NOT_READY"
    assert (tmp_path / "results" / "dataset_registry.json").is_file()
    assert (tmp_path / "results" / "performance" / "performance.json").is_file()
    assert (tmp_path / "paper" / "paper_manifest.json").is_file()
    assert not list((tmp_path / "paper").glob("Figure_*.png"))
    assert not list((tmp_path / "paper").glob("Table_*.csv"))

    performance = json.loads((tmp_path / "results" / "performance" / "performance.json").read_text(encoding="utf-8"))
    assert all(value is None for value in performance["measurements"].values())
