"""Run configured computational conditions through the existing CPG runner.

This module is an execution bridge, not a second simulation engine. Every
condition is delegated to ``run_locomotion`` and every calibration score is
delegated to the existing calibration utilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import re
from typing import Any, Callable, Iterable, Mapping

import yaml

from drosophila_pd.anatomy.audit import git_commit, runtime_environment
from drosophila_pd.experiments.healthy_baseline import (
    HealthyBaselineConfig,
    run_locomotion,
)
from drosophila_pd.parkinson import (
    DiseaseLayer,
    calibrate_candidates,
    load_phenotype_database,
)


SCIENTIFIC_SCOPE = (
    "This runner executes generic computational control conditions through the "
    "existing FlyGym CPG pipeline. It does not establish a biological disease "
    "model, clinical interpretation, or treatment response."
)

ConditionRunner = Callable[
    [HealthyBaselineConfig, DiseaseLayer | None, str], dict[str, Any]
]


@dataclass(frozen=True)
class CalibrationCondition:
    """One validated, named computational condition."""

    condition_id: str
    layer: DiseaseLayer
    description: str | None = None

    def to_mapping(self) -> dict[str, Any]:
        return {
            "condition_id": self.condition_id,
            "description": self.description,
            "disease_layer": self.layer.metadata(),
        }


def load_calibration_conditions(path: str | Path) -> tuple[CalibrationCondition, ...]:
    """Load and validate a YAML condition list."""

    source = Path(path)
    with source.open("r", encoding="utf-8") as handle:
        document = yaml.safe_load(handle) or {}
    if not isinstance(document, dict):
        raise ValueError("Calibration condition root must be a mapping.")
    raw_conditions = document.get("conditions")
    if not isinstance(raw_conditions, list) or not raw_conditions:
        raise ValueError("Calibration configuration requires a non-empty conditions list.")

    conditions: list[CalibrationCondition] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_conditions):
        if not isinstance(raw, dict):
            raise ValueError(f"conditions[{index}] must be a mapping.")
        condition_id = raw.get("condition_id", raw.get("id"))
        if not isinstance(condition_id, str) or not condition_id.strip():
            raise ValueError(f"conditions[{index}] requires a non-empty id.")
        condition_id = condition_id.strip()
        if condition_id in seen:
            raise ValueError(f"Duplicate calibration condition id: {condition_id}")
        seen.add(condition_id)
        layer_data = raw.get("disease_layer", raw)
        if not isinstance(layer_data, dict):
            raise ValueError(f"conditions[{index}].disease_layer must be a mapping.")
        layer = DiseaseLayer.from_mapping(layer_data)
        conditions.append(
            CalibrationCondition(
                condition_id=condition_id,
                layer=layer,
                description=(
                    None if raw.get("description") is None else str(raw["description"])
                ),
            )
        )
    return tuple(conditions)


def run_calibration_conditions(
    *,
    baseline_config: HealthyBaselineConfig,
    conditions: Iterable[CalibrationCondition],
    output_dir: str | Path,
    repo_root: str | Path | None = None,
    targets_path: str | Path | None = None,
    condition_runner: ConditionRunner | None = None,
) -> dict[str, Any]:
    """Run baseline and computational conditions, then optionally calibrate.

    The default runner executes the existing FlyGym simulation. The injectable
    runner is only for unit tests and does not change the production CLI path.
    """

    condition_list = tuple(conditions)
    if not condition_list:
        raise ValueError("At least one calibration condition is required.")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    runner = condition_runner or _default_condition_runner(repo_root)

    baseline_report = runner(baseline_config, None, "healthy_baseline")
    baseline_path = output / "healthy_baseline.json"
    _write_json(baseline_path, baseline_report)

    reports: list[dict[str, Any]] = []
    for condition in condition_list:
        report_path = output / f"{_safe_filename(condition.condition_id)}.json"
        report: dict[str, Any]
        try:
            report = runner(baseline_config, condition.layer, condition.condition_id)
            status = "PASS" if report.get("overall_pass") is True else "FAILED"
            error = None
        except Exception as exc:  # noqa: BLE001 - preserve failed condition audit
            report = {
                "condition_id": condition.condition_id,
                "overall_pass": False,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "scientific_scope": SCIENTIFIC_SCOPE,
            }
            status = "FAILED"
            error = f"{type(exc).__name__}: {exc}"
        _write_json(report_path, report)
        reports.append(
            {
                "condition_id": condition.condition_id,
                "status": status,
                "report": report_path.as_posix(),
                "parameters": condition.layer.metadata()["parameters"],
                "error": error,
                "metrics": dict(report.get("derived_locomotion_metrics", {})),
            }
        )

    calibration: dict[str, Any]
    if targets_path is None:
        calibration = {
            "status": "NOT_REQUESTED",
            "reason": "No phenotype target database was supplied.",
        }
    else:
        database = load_phenotype_database(targets_path)
        candidate_records = [
            (item["parameters"], item["metrics"])
            for item in reports
            if item["status"] == "PASS"
        ]
        result = calibrate_candidates(
            candidate_records,
            database.targets,
            provenance={
                "targets_path": str(Path(targets_path).resolve()),
                "simulation_runner": "drosophila_pd.experiments.healthy_baseline.run_locomotion",
                "failed_conditions_excluded": True,
            },
        )
        calibration = result.to_mapping()
        _write_json(output / "calibration.json", calibration)

    summary = {
        "schema_version": "1.0",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "git_commit": git_commit(repo_root),
        "environment": runtime_environment(),
        "baseline": {
            "condition_id": "healthy_baseline",
            "report": baseline_path.as_posix(),
            "overall_pass": baseline_report.get("overall_pass") is True,
        },
        "conditions": reports,
        "calibration": calibration,
        "counts": {
            "requested": len(reports),
            "passed": sum(item["status"] == "PASS" for item in reports),
            "failed": sum(item["status"] == "FAILED" for item in reports),
        },
        "overall_pass": bool(baseline_report.get("overall_pass") is True)
        and all(item["status"] == "PASS" for item in reports),
        "scientific_scope": SCIENTIFIC_SCOPE,
    }
    _write_json(output / "summary.json", summary)
    return summary


def _default_condition_runner(repo_root: str | Path | None) -> ConditionRunner:
    def runner(
        config: HealthyBaselineConfig,
        layer: DiseaseLayer | None,
        condition_id: str,
    ) -> dict[str, Any]:
        return run_locomotion(
            config,
            repo_root=repo_root,
            perturbation=layer,
            condition_id=condition_id,
            include_condition_metadata=True,
        )

    return runner


def _safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    if not cleaned:
        raise ValueError("Condition id does not contain a usable filename.")
    return cleaned


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


__all__ = [
    "CalibrationCondition",
    "ConditionRunner",
    "SCIENTIFIC_SCOPE",
    "load_calibration_conditions",
    "run_calibration_conditions",
]
