from __future__ import annotations

from pathlib import Path

from drosophila_pd.experiments.calibration_runner import load_calibration_conditions
from drosophila_pd.experiments.experimental_campaign import CampaignConfig


ROOT = Path(__file__).resolve().parents[1]


def test_computational_pd_like_demo_uses_existing_control_proxies():
    conditions = load_calibration_conditions(
        ROOT / "configs" / "parkinson" / "computational_pd_like_demo.yaml"
    )

    assert len(conditions) == 1
    layer = conditions[0].layer
    assert layer.motor_vigor == 0.8
    assert layer.coordination == 0.75
    assert layer.initiation_delay_steps == 300
    assert layer.action_latency_steps == 100
    assert layer.freezing_probability == 0.0006
    assert layer.freezing_duration_steps == 250
    assert layer.metadata()["scientific_scope"]


def test_campaign_can_enable_existing_latency_and_freezing_proxies():
    config = CampaignConfig.from_mapping(
        {
            "campaign_name": "unit_condition_mapping",
            "random_seeds": [0],
            "steps": 10,
            "duration_s": 0.01,
            "proxies": {
                "latency": {
                    "enabled": True,
                    "parameter": "action_latency_steps",
                    "values": [3],
                },
                "freezing": {
                    "enabled": True,
                    "parameter": "freezing_probability",
                    "values": [0.1],
                    "freezing_duration_steps": 2,
                },
            },
        }
    )

    latency, freezing = config.enabled_proxies
    assert latency.layer(3, 0, "latency_3").action_latency_steps == 3
    assert freezing.layer(0.1, 0, "freezing_01").freezing_duration_steps == 2
