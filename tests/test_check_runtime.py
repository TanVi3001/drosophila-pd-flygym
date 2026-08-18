"""Regression tests for the read-only runtime preflight checker."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("check_runtime_under_test", ROOT / "scripts" / "check_runtime.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_version_constraint_parser_supports_project_constraints() -> None:
    assert MODULE._version_satisfies("1.26.4", ">=1.26")
    assert MODULE._version_satisfies("3.10.8", ">=3.8,<4")
    assert MODULE._version_satisfies("3.9.0", "==3.9.0")
    assert not MODULE._version_satisfies("3.13.0", "==3.12.0")
    assert not MODULE._version_satisfies("4.0.0", ">=3.8,<4")


def test_runtime_report_is_structured_and_checks_entry_points() -> None:
    report = MODULE.check_runtime(ROOT)
    payload = report.as_dict()

    assert payload["repository_root"] == str(ROOT.resolve())
    assert isinstance(payload["checks"], list)
    names = {check["name"] for check in payload["checks"]}
    assert "Python" in names
    assert "FlyGym" in names
    assert "MuJoCo" in names
    assert "Canonical FlyGym locomotion helper" in names
    assert "Repository file: scripts/run_demo.py" in names
    assert "Repository file: scripts/generate_research_dataset.py" in names
    assert "Repository file: scripts/run_experiment_suite.py" in names
    assert set(payload["readiness"]) == {
        "runtime",
        "demo",
        "dataset_generation",
        "experiment_suite",
    }


def test_checker_does_not_write_files(tmp_path: Path) -> None:
    before = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))
    MODULE.check_runtime(tmp_path)
    after = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))
    assert after == before
