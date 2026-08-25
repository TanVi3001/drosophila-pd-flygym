"""Regression tests for Sprint 5 calibration experiment reporting."""

from __future__ import annotations

import json
from pathlib import Path

from drosophila_pd.experiments.calibration_experiment import (
    PASS,
    WAITING_RUNTIME,
    RuntimeGate,
    build_comparison_rows,
    build_loss_rows,
    build_response_curve_rows,
    run_calibration_experiment,
    write_figures,
)
from drosophila_pd.experiments.healthy_baseline import HealthyBaselineConfig
from drosophila_pd.experiments.parameter_sweep import load_parameter_sweep_config


ROOT = Path(__file__).parents[1]


def _ready_gate() -> RuntimeGate:
    return RuntimeGate(
        runtime_ready=True,
        runtime_report={"readiness": {"runtime": True}},
        target_ready=True,
        target_report={"ready": True, "numeric_target_count": 1},
    )


def _report() -> dict:
    baseline = {
        "derived_locomotion_metrics": {
            "mean_planar_speed_mm_s": 10.0,
            "trajectory_efficiency": 0.8,
            "heading_variance_rad2": 0.2,
            "heading_yaw_change_rad": 0.1,
        }
    }
    def condition(identifier, family, parameter, speed, heading, efficiency):
        return {
            "condition_id": identifier,
            "family": family,
            "parameter_name": "scale",
            "parameter_value": parameter,
            "status": "completed",
            "overall_pass": True,
            "perturbation": {"parameters": {"motor_vigor": parameter, "coordination": parameter}},
            "report": {
                "derived_locomotion_metrics": {
                    "mean_planar_speed_mm_s": speed,
                    "trajectory_efficiency": efficiency,
                    "heading_variance_rad2": heading,
                    "heading_yaw_change_rad": 0.1,
                }
            },
        }
    return {
        "baseline": baseline,
        "conditions": [
            condition("vigor_080", "motor_vigor", 0.8, 8.0, 0.3, 0.7),
            condition("coordination_075", "coordination", 0.75, 9.0, 0.4, 0.6),
        ],
        "overall_pass": True,
    }


def test_reporting_uses_only_available_metrics_and_builds_losses(tmp_path: Path):
    report = _report()
    curves = build_response_curve_rows(report)
    assert any(row["curve_id"] == "speed_vs_motor_vigor" and row["status"] == PASS for row in curves)
    assert any(row["curve_id"] == "heading_variance_vs_coordination" and row["status"] == PASS for row in curves)
    comparison = build_comparison_rows(report)
    losses = build_loss_rows(report)
    assert comparison
    assert losses[0]["status"] == PASS
    assert losses[0]["rmse"] is not None
    assert losses[0]["cosine"] is not None
    figures = write_figures(tmp_path / "figures", curves, comparison, losses)
    assert "speed_vs_motor_vigor" in figures
    assert "heading_variance_vs_coordination" in figures
    assert "trajectory_efficiency_vs_coordination" in figures
    assert "metric_comparison" in figures
    assert "calibration_trend" in figures


def test_missing_requested_metric_is_explicitly_unavailable():
    report = _report()
    report["conditions"][1]["report"]["derived_locomotion_metrics"].pop("heading_variance_rad2")
    report["conditions"][1]["report"]["derived_locomotion_metrics"].pop("heading_yaw_change_rad")
    curves = build_response_curve_rows(report)
    row = next(item for item in curves if item["curve_id"] == "heading_variance_vs_coordination")
    assert row["status"] == "UNAVAILABLE_METRIC"
    assert row["metric_value"] is None


def test_runner_stops_at_waiting_runtime_without_scientific_outputs(tmp_path: Path):
    target = tmp_path / "targets.json"
    target.write_text(json.dumps({"schema_version": "1.0", "metadata": {}, "targets": []}), encoding="utf-8")
    output = tmp_path / "output"
    payload = run_calibration_experiment(
        baseline_config=ROOT / "configs" / "experiments" / "healthy_baseline.yaml",
        sweep_config=ROOT / "configs" / "parkinson" / "calibration_experiment.yaml",
        target_path=target,
        output_dir=output,
        repo_root=ROOT,
        runtime_gate=RuntimeGate(
            runtime_ready=False,
            runtime_report={"readiness": {"runtime": False}},
            target_ready=False,
            target_report={"ready": False, "status": "WAITING_DATASET"},
        ),
    )
    assert payload["status"] == WAITING_RUNTIME
    assert payload["scientific_results_generated"] is False
    assert (output / "status.json").is_file()
    assert (output / "sensitivity.csv").read_text(encoding="utf-8").startswith("condition_id")
    assert not (output / "figures").exists()


def test_sweep_configuration_contains_only_requested_families():
    config = load_parameter_sweep_config(ROOT / "configs" / "parkinson" / "calibration_experiment.yaml")
    assert {family.family for family in config.families} == {"motor_vigor", "coordination"}
    assert config.conditions()
