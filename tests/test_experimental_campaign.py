"""Regression tests cho Experimental Campaign v1 khong chay simulation."""

from __future__ import annotations

from pathlib import Path

from drosophila_pd.experiments.calibration_experiment import RuntimeGate
from drosophila_pd.experiments.experimental_campaign import (
    PASS,
    WAITING_RUNTIME,
    WAITING_TARGET_DATA,
    build_parameter_sensitivity,
    build_response_surface,
    load_campaign_config,
    run_experimental_campaign,
)


ROOT = Path(__file__).resolve().parents[1]


def _gate(*, runtime: bool, target: bool) -> RuntimeGate:
    return RuntimeGate(
        runtime_ready=runtime,
        runtime_report={"readiness": {"runtime": runtime}},
        target_ready=target,
        target_report={"ready": target},
    )


def _write_campaign(path: Path) -> None:
    path.write_text(
        """
campaign_name: test_campaign
random_seeds: [0, 1]
steps: 2
duration_s: 0.0002
output_directory: results/experimental_campaign
proxies:
  motor_vigor:
    enabled: true
    parameter: motor_vigor
    values: [0.8, 1.0]
  coordination:
    enabled: false
    parameter: coordination
    values: [0.75]
  noise: {enabled: false, parameter: motor_noise_std, values: [0.01]}
  delay: {enabled: false, parameter: initiation_delay_steps, values: [1]}
  fatigue: {enabled: false, parameter: fatigue_rate, values: [0.01]}
  latency: {enabled: false, values: []}
  freezing: {enabled: false, values: []}
  asymmetry: {enabled: false, parameter: asymmetry, values: [0.0]}
  postural_instability: {enabled: false, values: []}
""".strip()
        + "\n",
        encoding="utf-8",
    )


def _condition_runner(config, layer, condition_id):
    vigor = 1.0 if layer is None else layer.motor_vigor
    return {
        "overall_pass": True,
        "derived_locomotion_metrics": {
            "mean_planar_speed_mm_s": 10.0 * vigor,
            "planar_path_length_mm": 2.0 * vigor,
            "trajectory_efficiency": vigor,
        },
    }


def test_runtime_gate_stops_without_scientific_artifacts(tmp_path):
    campaign = tmp_path / "campaign.yaml"
    _write_campaign(campaign)
    output = tmp_path / "output"

    payload = run_experimental_campaign(
        campaign_config=campaign,
        baseline_config=ROOT / "configs/experiments/healthy_baseline.yaml",
        target_path=tmp_path / "targets.json",
        output_dir=output,
        repo_root=ROOT,
        runtime_gate=_gate(runtime=False, target=False),
        condition_runner=_condition_runner,
    )

    assert payload["status"] == WAITING_RUNTIME
    assert payload["runtime_status"] == WAITING_RUNTIME
    assert payload["target_status"] == WAITING_TARGET_DATA
    assert payload["gate"]["overall_status"] == WAITING_RUNTIME
    assert (output / "campaign_status.json").is_file()
    assert not (output / "response_surface.csv").exists()


def test_target_gate_is_reported_after_runtime_pass(tmp_path):
    campaign = tmp_path / "campaign.yaml"
    _write_campaign(campaign)

    payload = run_experimental_campaign(
        campaign_config=campaign,
        baseline_config=ROOT / "configs/experiments/healthy_baseline.yaml",
        target_path=tmp_path / "targets.json",
        output_dir=tmp_path / "output",
        repo_root=ROOT,
        runtime_gate=_gate(runtime=True, target=False),
        condition_runner=_condition_runner,
    )

    assert payload["status"] == WAITING_TARGET_DATA
    assert payload["runtime_status"] == PASS
    assert payload["gate"]["overall_status"] == WAITING_TARGET_DATA


def test_success_path_writes_real_campaign_artifacts_without_simulation(tmp_path):
    campaign = tmp_path / "campaign.yaml"
    _write_campaign(campaign)
    output = tmp_path / "output"

    payload = run_experimental_campaign(
        campaign_config=campaign,
        baseline_config=ROOT / "configs/experiments/healthy_baseline.yaml",
        target_path=tmp_path / "targets.json",
        output_dir=output,
        repo_root=ROOT,
        runtime_gate=_gate(runtime=True, target=True),
        condition_runner=_condition_runner,
    )

    assert payload["status"] == PASS
    assert payload["counts"] == {"completed": 6, "failed": 0, "waiting": 0}
    for filename in (
        "campaign_data.json",
        "campaign_status.json",
        "response_surface.csv",
        "response_surface.json",
        "response_surface.md",
        "parameter_sensitivity.csv",
        "parameter_sensitivity.md",
        "experiment_summary.md",
    ):
        assert (output / filename).is_file(), filename


def test_response_surface_and_sensitivity_use_available_metrics_only():
    campaign = {
        "config": {
            "proxies": {
                "motor_vigor": {"enabled": True, "values": [0.8, 1.0]},
                "coordination": {"enabled": False, "values": []},
            }
        },
        "baseline": [
            {
                "status": "COMPLETED",
                "metrics": {
                    "mean_planar_speed_mm_s": 10.0,
                    "planar_path_length_mm": 2.0,
                    "trajectory_efficiency": 1.0,
                },
            }
        ],
        "conditions": [
            {
                "status": "COMPLETED",
                "proxy": "motor_vigor",
                "parameter_value": 0.8,
                "metrics": {
                    "mean_planar_speed_mm_s": 8.0,
                    "planar_path_length_mm": 1.6,
                    "trajectory_efficiency": 0.8,
                },
            },
            {
                "status": "FAILED",
                "proxy": "motor_vigor",
                "parameter_value": 1.0,
                "metrics": {"mean_planar_speed_mm_s": 999.0},
            },
        ],
    }

    surface = build_response_surface(campaign)
    speed = next(
        row
        for row in surface["rows"]
        if row["metric"] == "walking_speed" and row["parameter_value"] == 0.8
    )
    missing = next(
        row
        for row in surface["rows"]
        if row["metric"] == "heading_variance" and row["parameter_value"] == 0.8
    )
    assert speed["mean"] == 8.0
    assert speed["healthy_mean"] == 10.0
    assert missing["status"] == "UNAVAILABLE_METRIC"
    assert missing["mean"] is None

    sensitivity = build_parameter_sensitivity(surface)
    row = next(item for item in sensitivity["rows"] if item["parameter"] == "motor_vigor")
    assert row["status"] == PASS
    assert row["rank"] == 1
    assert row["point_count"] == 3


def test_default_campaign_has_only_supported_enabled_proxies():
    config = load_campaign_config(ROOT / "configs/experiments/campaign_v1.yaml")
    assert {item.proxy for item in config.enabled_proxies} == {"motor_vigor", "coordination"}
