from pathlib import Path

from drosophila_pd.experiments.calibration_runner import load_calibration_conditions


ROOT = Path(__file__).parents[1]


def test_sensitivity_grid_is_reproducible_and_scoped():
    conditions = load_calibration_conditions(
        ROOT / "configs" / "parkinson" / "sensitivity_grid.yaml"
    )

    assert len(conditions) == 10
    assert len({condition.condition_id for condition in conditions}) == 10
    assert {condition.layer.motor_vigor for condition in conditions} >= {0.6, 0.7, 0.8, 0.9}
    assert {condition.layer.coordination for condition in conditions} >= {0.6, 0.75, 0.9}
    assert {condition.layer.initiation_delay_steps for condition in conditions} >= {0, 5, 10}
    assert all("disease" not in condition.condition_id.lower() for condition in conditions)
