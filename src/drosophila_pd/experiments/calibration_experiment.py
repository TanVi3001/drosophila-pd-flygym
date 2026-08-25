"""Evidence-gated calibration experiment reporting.

This module orchestrates the existing parameter-sweep and calibration APIs. It
does not introduce a simulation engine, a Disease Layer proxy, or an optimizer.
Production results are created only after the real runtime and a numeric,
provenance-bearing target dataset are available.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import UTC, datetime
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable, Iterable, Mapping, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from drosophila_pd.parkinson import calibrate_candidates, load_phenotype_database
from drosophila_pd.experiments.healthy_baseline import (
    HealthyBaselineConfig,
    load_healthy_baseline_config,
)
from drosophila_pd.experiments.parameter_sweep import (
    ParameterSweepConfig,
    load_parameter_sweep_config,
    run_parameter_sweep,
)


WAITING_RUNTIME = "WAITING_RUNTIME"
PASS = "PASS"
FAILED = "FAILED"
PARTIAL = "PARTIAL_METRICS"

SCIENTIFIC_SCOPE = (
    "This workflow reports generic computational response curves and metric "
    "comparisons from the existing FlyGym experiment runner. It is not a "
    "Parkinson model, biological validation, diagnosis, or treatment result."
)

RESPONSE_SPECS: tuple[dict[str, Any], ...] = (
    {
        "curve_id": "speed_vs_motor_vigor",
        "family": "motor_vigor",
        "metric": "mean_planar_speed_mm_s",
        "label": "Mean planar speed (mm/s)",
    },
    {
        "curve_id": "heading_variance_vs_coordination",
        "family": "coordination",
        "metric": "heading_variance_rad2",
        "metric_aliases": ("heading_variance", "body_orientation_variance_rad2"),
        "label": "Heading variance (rad2)",
    },
    {
        "curve_id": "trajectory_efficiency_vs_coordination",
        "family": "coordination",
        "metric": "trajectory_efficiency",
        "label": "Trajectory efficiency", 
    },
)

COMPARISON_METRICS: tuple[str, ...] = (
    "mean_planar_speed_mm_s",
    "planar_displacement_mm",
    "planar_path_length_mm",
    "trajectory_efficiency",
    "heading_yaw_change_rad",
    "heading_variance_rad2",
    "body_orientation_variance_rad2",
)

@dataclass(frozen=True)
class RuntimeGate:
    """Machine-readable runtime and target-dataset gate state."""

    runtime_ready: bool
    runtime_report: Mapping[str, Any]
    target_ready: bool
    target_report: Mapping[str, Any]

    @property
    def ready(self) -> bool:
        return self.runtime_ready and self.target_ready

    def to_mapping(self) -> dict[str, Any]:
        return {
            "runtime_ready": self.runtime_ready,
            "runtime": dict(self.runtime_report),
            "target_ready": self.target_ready,
            "target_dataset": dict(self.target_report),
            "overall_status": PASS if self.ready else WAITING_RUNTIME,
        }


def run_calibration_experiment(
    *,
    baseline_config: str | Path,
    sweep_config: str | Path,
    target_path: str | Path,
    output_dir: str | Path,
    repo_root: str | Path | None = None,
    runtime_gate: RuntimeGate | None = None,
    condition_runner: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run the evidence-gated calibration workflow and write its artifacts.

    ``condition_runner`` exists for deterministic unit tests only. The CLI uses
    the existing FlyGym runner through :func:`run_parameter_sweep`.
    """

    root = Path(repo_root or Path.cwd()).expanduser().resolve()
    output = Path(output_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    baseline = load_healthy_baseline_config(baseline_config)
    sweep = load_parameter_sweep_config(sweep_config)
    gate = runtime_gate or build_runtime_gate(root, target_path)

    if not gate.ready:
        return write_waiting_artifacts(
            output,
            gate=gate,
            baseline_config=baseline,
            sweep_config=sweep,
            target_path=target_path,
            repo_root=root,
        )

    try:
        sweep_report = run_parameter_sweep(
            baseline_config=baseline,
            sweep_config=sweep,
            repo_root=root,
            condition_runner=condition_runner,
        )
    except Exception as error:  # preserve an auditable failed workflow
        return write_failed_artifacts(
            output,
            gate=gate,
            baseline_config=baseline,
            sweep_config=sweep,
            target_path=target_path,
            repo_root=root,
            error=error,
        )

    sweep_path = _write_json(output / "sweep_report.json", sweep_report)
    response_rows = build_response_curve_rows(sweep_report)
    sensitivity_rows = build_sensitivity_rows(sweep_report)
    comparison_rows = build_comparison_rows(sweep_report)
    loss_rows = build_loss_rows(sweep_report)
    paths = {
        "sweep_report": sweep_path,
        "response_curves": _write_csv(output / "response_curves.csv", response_rows),
        "sensitivity": _write_csv(output / "sensitivity.csv", sensitivity_rows),
        "comparison": _write_csv(output / "comparison.csv", comparison_rows),
        "loss": _write_csv(output / "loss.csv", loss_rows),
    }

    target_database = load_phenotype_database(target_path)
    candidate_records = _candidate_records(sweep_report)
    calibration_result = calibrate_candidates(
        candidate_records,
        target_database.targets,
        provenance={
            "target_path": str(Path(target_path).resolve()),
            "sweep_report": str(sweep_path),
            "simulation_runner": "drosophila_pd.experiments.parameter_sweep",
        },
    )
    paths["calibration"] = _write_json(
        output / "calibration.json", calibration_result.to_mapping()
    )

    figure_paths = write_figures(
        output / "figures", response_rows, comparison_rows, loss_rows
    )
    paths.update({f"figure_{key}": value for key, value in figure_paths.items()})

    response_status = _status_from_rows(response_rows)
    overall_status = PASS if sweep_report.get("overall_pass") and response_status == PASS else PARTIAL
    payload = {
        "schema_version": "1.0",
        "status": overall_status,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "gate": gate.to_mapping(),
        "target_path": str(Path(target_path).resolve()),
        "sweep_report": str(sweep_path),
        "calibration_status": calibration_result.status,
        "response_status": response_status,
        "artifacts": {key: path.as_posix() for key, path in paths.items()},
        "figure_count": len(figure_paths),
        "scientific_scope": SCIENTIFIC_SCOPE,
    }
    _write_json(output / "status.json", payload)
    _write_markdown_reports(output, payload, sensitivity_rows, comparison_rows, loss_rows)
    return payload


def build_runtime_gate(
    repo_root: str | Path,
    target_path: str | Path,
) -> RuntimeGate:
    """Run the repository's read-only runtime checker and inspect targets."""

    root = Path(repo_root).expanduser().resolve()
    runtime_report = _run_runtime_checker(root)
    target_report = _inspect_target_dataset(target_path)
    return RuntimeGate(
        runtime_ready=bool(runtime_report.get("readiness", {}).get("runtime", False)),
        runtime_report=runtime_report,
        target_ready=bool(target_report.get("ready", False)),
        target_report=target_report,
    )


def build_response_curve_rows(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Extract requested response curves without substituting unavailable metrics."""

    rows: list[dict[str, Any]] = []
    for spec in RESPONSE_SPECS:
        conditions = [
            item
            for item in report.get("conditions", [])
            if item.get("family") == spec["family"]
            and item.get("status") == "completed"
        ]
        for condition in conditions:
            metrics = _condition_metrics(condition)
            metric_name, value = _first_finite_metric(
                metrics, (spec["metric"], *spec.get("metric_aliases", ()))
            )
            baseline_metrics = _baseline_metrics(report)
            _, baseline_value = _first_finite_metric(
                baseline_metrics, (spec["metric"], *spec.get("metric_aliases", ()))
            )
            rows.append(
                {
                    "curve_id": spec["curve_id"],
                    "family": spec["family"],
                    "condition_id": condition.get("condition_id", ""),
                    "parameter_name": condition.get("parameter_name", ""),
                    "parameter_value": condition.get("parameter_value"),
                    "metric_requested": spec["metric"],
                    "metric_used": metric_name or "",
                    "metric_value": value,
                    "baseline_value": baseline_value,
                    "absolute_delta": _delta(value, baseline_value),
                    "status": "PASS" if value is not None else "UNAVAILABLE_METRIC",
                }
            )
    return rows


def build_sensitivity_rows(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build parameter-to-metric sensitivity rows from completed conditions."""

    rows: list[dict[str, Any]] = []
    baseline = _baseline_metrics(report)
    for condition in report.get("conditions", []):
        if condition.get("status") != "completed":
            continue
        metrics = _condition_metrics(condition)
        for metric in COMPARISON_METRICS:
            value = _finite_or_none(metrics.get(metric))
            baseline_value = _finite_or_none(baseline.get(metric))
            rows.append(
                {
                    "condition_id": condition.get("condition_id", ""),
                    "family": condition.get("family", ""),
                    "parameter_name": condition.get("parameter_name", ""),
                    "parameter_value": condition.get("parameter_value"),
                    "metric": metric,
                    "baseline_value": baseline_value,
                    "condition_value": value,
                    "absolute_delta": _delta(value, baseline_value),
                    "relative_delta": _relative_delta(value, baseline_value),
                    "status": "PASS" if value is not None else "UNAVAILABLE_METRIC",
                }
            )
    return rows


def build_comparison_rows(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build Healthy/Candidate/Difference rows without biological interpretation."""

    rows: list[dict[str, Any]] = []
    for row in build_sensitivity_rows(report):
        rows.append(
            {
                "condition_id": row["condition_id"],
                "family": row["family"],
                "parameter_name": row["parameter_name"],
                "parameter_value": row["parameter_value"],
                "metric": row["metric"],
                "healthy": row["baseline_value"],
                "candidate": row["condition_value"],
                "difference": row["absolute_delta"],
                "relative_difference": row["relative_delta"],
                "status": row["status"],
            }
        )
    return rows


def build_loss_rows(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Compute transparent vector losses against the Healthy baseline.

    Metrics are normalized by the absolute Healthy value per metric so that the
    report does not silently add quantities with incompatible physical units.
    The result is a computational difference report, not a biological score.
    """

    baseline = _baseline_metrics(report)
    rows: list[dict[str, Any]] = []
    for condition in report.get("conditions", []):
        if condition.get("status") != "completed":
            continue
        candidate = _condition_metrics(condition)
        names: list[str] = []
        base_values: list[float] = []
        candidate_values: list[float] = []
        for metric in COMPARISON_METRICS:
            base = _finite_or_none(baseline.get(metric))
            value = _finite_or_none(candidate.get(metric))
            if base is None or value is None:
                continue
            scale = abs(base) if abs(base) > 1e-12 else 1.0
            names.append(metric)
            base_values.append(base / scale)
            candidate_values.append(value / scale)
        if names:
            errors = [candidate_value - base_value for base_value, candidate_value in zip(base_values, candidate_values)]
            cosine_similarity = _cosine(base_values, candidate_values)
            rows.append(
                {
                    "condition_id": condition.get("condition_id", ""),
                    "family": condition.get("family", ""),
                    "parameter_value": condition.get("parameter_value"),
                    "metric_count": len(names),
                    "metrics": ";".join(names),
                    "rmse": math.sqrt(sum(error * error for error in errors) / len(errors)),
                    "mae": sum(abs(error) for error in errors) / len(errors),
                    "cosine": cosine_similarity,
                    "cosine_distance": 1.0 - cosine_similarity if cosine_similarity is not None else None,
                    "huber": sum(_huber(error, 1.0) for error in errors) / len(errors),
                    "normalization": "each metric divided by abs(Healthy), or 1 when Healthy is zero",
                    "status": PASS,
                }
            )
        else:
            rows.append(
                {
                    "condition_id": condition.get("condition_id", ""),
                    "family": condition.get("family", ""),
                    "parameter_value": condition.get("parameter_value"),
                    "metric_count": 0,
                    "metrics": "",
                    "rmse": None,
                    "mae": None,
                    "cosine": None,
                    "cosine_distance": None,
                    "huber": None,
                    "normalization": "not available",
                    "status": "UNAVAILABLE_METRICS",
                }
            )
    return rows


def write_figures(
    figure_dir: str | Path,
    response_rows: Sequence[Mapping[str, Any]],
    comparison_rows: Sequence[Mapping[str, Any]],
    loss_rows: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Path]:
    """Write figures only for finite metrics present in the real reports."""

    output = Path(figure_dir)
    output.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for curve_id in sorted({row["curve_id"] for row in response_rows}):
        rows = [
            row
            for row in response_rows
            if row["curve_id"] == curve_id and row["status"] == PASS
        ]
        if not rows:
            continue
        path = output / f"{curve_id}.png"
        figure, axis = plt.subplots(figsize=(7, 4.5), dpi=150)
        axis.plot(
            [float(row["parameter_value"]) for row in rows],
            [float(row["metric_value"]) for row in rows],
            marker="o",
        )
        axis.set_title(curve_id.replace("_", " ").title())
        axis.set_xlabel("Parameter value")
        axis.set_ylabel(str(rows[0]["metric_used"]))
        axis.grid(alpha=0.25)
        figure.tight_layout()
        figure.savefig(path)
        plt.close(figure)
        paths[curve_id] = path

    available = [row for row in comparison_rows if row.get("status") == PASS]
    if available:
        path = output / "metric_comparison.png"
        figure, axis = plt.subplots(figsize=(9, 5), dpi=150)
        labels = [f"{row['condition_id']}\n{row['metric']}" for row in available]
        differences = [float(row["difference"]) for row in available]
        axis.bar(range(len(labels)), differences)
        axis.set_title("Healthy versus candidate metric difference")
        axis.set_ylabel("Candidate - Healthy")
        axis.set_xticks(range(len(labels)), labels, rotation=75, ha="right", fontsize=7)
        axis.axhline(0.0, color="black", linewidth=0.8)
        axis.grid(axis="y", alpha=0.25)
        figure.tight_layout()
        figure.savefig(path)
        plt.close(figure)
        paths["metric_comparison"] = path
    available_losses = [row for row in loss_rows if row.get("status") == PASS]
    if available_losses:
        path = output / "calibration_trend.png"
        figure, axis = plt.subplots(figsize=(8, 4.5), dpi=150)
        for family in sorted({str(row.get("family", "")) for row in available_losses}):
            family_rows = [row for row in available_losses if row.get("family") == family]
            family_rows = sorted(family_rows, key=lambda row: float(row["parameter_value"]))
            axis.plot(
                [float(row["parameter_value"]) for row in family_rows],
                [float(row["rmse"]) for row in family_rows],
                marker="o",
                label=family,
            )
        axis.set_title("Calibration trend: normalized RMSE")
        axis.set_xlabel("Parameter value")
        axis.set_ylabel("Normalized RMSE vs Healthy")
        axis.grid(alpha=0.25)
        axis.legend()
        figure.tight_layout()
        figure.savefig(path)
        plt.close(figure)
        paths["calibration_trend"] = path
    return paths


def write_waiting_artifacts(
    output: Path,
    *,
    gate: RuntimeGate,
    baseline_config: HealthyBaselineConfig,
    sweep_config: ParameterSweepConfig,
    target_path: str | Path,
    repo_root: Path,
) -> dict[str, Any]:
    """Write an explicit waiting state without scientific result artifacts."""

    empty_rows = {
        "response_curves": [],
        "sensitivity": [],
        "comparison": [],
        "loss": [],
    }
    paths = {
        key: _write_csv(output / f"{key}.csv", rows)
        for key, rows in empty_rows.items()
    }
    payload = {
        "schema_version": "1.0",
        "status": WAITING_RUNTIME,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "gate": gate.to_mapping(),
        "target_path": str(Path(target_path).expanduser().resolve()),
        "baseline_config": baseline_config.to_report(),
        "sweep_config": sweep_config.to_report(),
        "artifacts": {key: path.as_posix() for key, path in paths.items()},
        "scientific_results_generated": False,
        "scientific_scope": SCIENTIFIC_SCOPE,
        "next_action": "Install the pinned runtime and provide an approved numeric target dataset, then rerun.",
    }
    _write_json(output / "status.json", payload)
    _write_markdown_reports(output, payload, [], [], [])
    return payload


def write_failed_artifacts(
    output: Path,
    *,
    gate: RuntimeGate,
    baseline_config: HealthyBaselineConfig,
    sweep_config: ParameterSweepConfig,
    target_path: str | Path,
    repo_root: Path,
    error: BaseException,
) -> dict[str, Any]:
    """Write an execution failure without treating it as a scientific result."""

    payload = {
        "schema_version": "1.0",
        "status": FAILED,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "gate": gate.to_mapping(),
        "target_path": str(Path(target_path).expanduser().resolve()),
        "baseline_config": baseline_config.to_report(),
        "sweep_config": sweep_config.to_report(),
        "error_type": type(error).__name__,
        "error": str(error),
        "scientific_results_generated": False,
        "scientific_scope": SCIENTIFIC_SCOPE,
    }
    _write_json(output / "status.json", payload)
    _write_markdown_reports(output, payload, [], [], [])
    return payload


def _run_runtime_checker(root: Path) -> dict[str, Any]:
    command = [sys.executable, str(root / "scripts" / "check_runtime.py"), "--root", str(root), "--json"]
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        payload = json.loads(completed.stdout or "{}")
        if isinstance(payload, dict):
            return payload
        return {"readiness": {"runtime": False}, "error": "Runtime checker returned a non-object."}
    except (OSError, json.JSONDecodeError) as error:
        return {"readiness": {"runtime": False}, "error_type": type(error).__name__, "error": str(error)}


def _inspect_target_dataset(path: str | Path) -> dict[str, Any]:
    source = Path(path).expanduser().resolve()
    if not source.is_file():
        return {"ready": False, "status": "WAITING_DATASET", "path": str(source), "numeric_target_count": 0, "reason": "Target dataset is missing."}
    try:
        database = load_phenotype_database(source)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        return {"ready": False, "status": "WAITING_DATASET", "path": str(source), "numeric_target_count": 0, "reason": f"Target dataset is not valid: {type(error).__name__}: {error}"}
    count = len(database.numeric_targets)
    return {
        "ready": count > 0,
        "status": PASS if count > 0 else "WAITING_DATASET",
        "path": str(source),
        "target_count": len(database.targets),
        "numeric_target_count": count,
        "reason": "Numeric targets are available." if count > 0 else "No approved numeric targets are available.",
    }


def _candidate_records(report: Mapping[str, Any]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    records: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for condition in report.get("conditions", []):
        if condition.get("status") != "completed" or condition.get("overall_pass") is not True:
            continue
        perturbation = condition.get("perturbation", {})
        parameters = perturbation.get("parameters", {}) if isinstance(perturbation, Mapping) else {}
        records.append((dict(parameters), dict(_condition_metrics(condition))))
    return records


def _baseline_metrics(report: Mapping[str, Any]) -> Mapping[str, Any]:
    baseline = report.get("baseline", {})
    return _nested_metrics(baseline)


def _condition_metrics(condition: Mapping[str, Any]) -> Mapping[str, Any]:
    report = condition.get("report", {})
    return _nested_metrics(report if isinstance(report, Mapping) else condition)


def _nested_metrics(report: Mapping[str, Any]) -> Mapping[str, Any]:
    metrics = report.get("derived_locomotion_metrics", report.get("metrics", report))
    return metrics if isinstance(metrics, Mapping) else {}


def _first_finite_metric(metrics: Mapping[str, Any], names: Iterable[str]) -> tuple[str | None, float | None]:
    for name in names:
        value = _finite_or_none(metrics.get(name))
        if value is not None:
            return name, value
    return None, None


def _status_from_rows(rows: Sequence[Mapping[str, Any]]) -> str:
    if not rows or not any(row.get("status") == PASS for row in rows):
        return "UNAVAILABLE_METRICS"
    return PASS if all(row.get("status") == PASS for row in rows) else PARTIAL


def _finite_or_none(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _delta(value: float | None, baseline: float | None) -> float | None:
    return None if value is None or baseline is None else value - baseline


def _relative_delta(value: float | None, baseline: float | None) -> float | None:
    if value is None or baseline is None or abs(baseline) <= 1e-12:
        return None
    return (value - baseline) / abs(baseline)


def _cosine(left: Sequence[float], right: Sequence[float]) -> float | None:
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm <= 1e-12 or right_norm <= 1e-12:
        return None
    return sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)


def _huber(error: float, delta: float) -> float:
    magnitude = abs(error)
    return 0.5 * error * error if magnitude <= delta else delta * (magnitude - 0.5 * delta)


def _write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return path


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        fields = list(rows[0].keys())
    else:
        fields = {
            "response_curves": ["curve_id", "family", "condition_id", "parameter_name", "parameter_value", "metric_requested", "metric_used", "metric_value", "baseline_value", "absolute_delta", "status"],
            "sensitivity": ["condition_id", "family", "parameter_name", "parameter_value", "metric", "baseline_value", "condition_value", "absolute_delta", "relative_delta", "status"],
            "comparison": ["condition_id", "family", "parameter_name", "parameter_value", "metric", "healthy", "candidate", "difference", "relative_difference", "status"],
            "loss": ["condition_id", "family", "parameter_value", "metric_count", "metrics", "rmse", "mae", "cosine", "cosine_distance", "huber", "normalization", "status"],
        }.get(path.stem, ["status"])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path


def _write_markdown_reports(
    output: Path,
    payload: Mapping[str, Any],
    sensitivity_rows: Sequence[Mapping[str, Any]],
    comparison_rows: Sequence[Mapping[str, Any]],
    loss_rows: Sequence[Mapping[str, Any]],
) -> None:
    status = payload.get("status", WAITING_RUNTIME)
    scope = payload.get("scientific_scope", SCIENTIFIC_SCOPE)
    waiting = status == WAITING_RUNTIME
    sensitivity = [
        "# Sensitivity Report",
        "",
        f"- Status: `{status}`",
        "- Sensitivity is a computational response description, not a biological conclusion.",
        "",
        "| Condition | Family | Parameter | Metric | Healthy | Candidate | Difference | Status |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    sensitivity.extend(_markdown_rows(sensitivity_rows, ("condition_id", "family", "parameter_value", "metric", "baseline_value", "condition_value", "absolute_delta", "status")))
    if not sensitivity_rows:
        sensitivity.append("| - | - | - | - | - | - | - | WAITING_RUNTIME |")
    (output / "sensitivity.md").write_text("\n".join(sensitivity) + "\n", encoding="utf-8")

    comparison = [
        "# Comparison Report",
        "",
        f"- Status: `{status}`",
        "- Healthy is the computational baseline; candidate rows are not disease labels.",
        "",
        "| Condition | Family | Metric | Healthy | Candidate | Difference | Relative difference | Status |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    comparison.extend(_markdown_rows(comparison_rows, ("condition_id", "family", "metric", "healthy", "candidate", "difference", "relative_difference", "status")))
    if not comparison_rows:
        comparison.append("| - | - | - | - | - | - | - | WAITING_RUNTIME |")
    (output / "comparison.md").write_text("\n".join(comparison) + "\n", encoding="utf-8")

    loss = [
        "# Loss Report",
        "",
        f"- Status: `{status}`",
        "- Losses compare candidate metrics to the Healthy baseline only.",
        "- Each metric is normalized by its Healthy absolute value before aggregation; this is a computational diagnostic, not a biological score.",
        "",
        "| Condition | Family | Metric count | RMSE | MAE | Cosine | Huber | Status |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    loss.extend(_markdown_rows(loss_rows, ("condition_id", "family", "metric_count", "rmse", "mae", "cosine", "huber", "status")))
    if not loss_rows:
        loss.append("| - | - | 0 | - | - | - | - | WAITING_RUNTIME |")
    (output / "loss.md").write_text("\n".join(loss) + "\n", encoding="utf-8")

    report = [
        "# Calibration Experiment Status",
        "",
        f"- Status: `{status}`",
        f"- Scientific scope: {scope}",
        "",
    ]
    if waiting:
        report.extend([
            "No simulation, response curve, loss, comparison, or figure was generated.",
            "The workflow is waiting for the pinned FlyGym runtime and an approved numeric target dataset.",
        ])
    else:
        report.extend([
            f"- Response rows: `{len(payload.get('artifacts', {}))}` artifacts were written.",
            f"- Figures: `{payload.get('figure_count', 0)}`",
            "- See `sensitivity.md`, `comparison.md`, and `loss.md` for metric-level results.",
        ])
    (output / "calibration_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def _markdown_rows(rows: Sequence[Mapping[str, Any]], fields: Sequence[str]) -> list[str]:
    return ["| " + " | ".join(_display(row.get(field)) for field in fields) + " |" for row in rows]


def _display(value: Any) -> str:
    if value is None or value == "":
        return "-"
    if isinstance(value, float):
        return f"{value:.8g}"
    return str(value).replace("|", "\\|")


__all__ = [
    "COMPARISON_METRICS",
    "FAILED",
    "PARTIAL",
    "PASS",
    "RESPONSE_SPECS",
    "RuntimeGate",
    "SCIENTIFIC_SCOPE",
    "WAITING_RUNTIME",
    "build_comparison_rows",
    "build_loss_rows",
    "build_response_curve_rows",
    "build_runtime_gate",
    "build_sensitivity_rows",
    "run_calibration_experiment",
    "write_figures",
]
