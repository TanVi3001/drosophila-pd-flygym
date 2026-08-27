from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np
import pytest

from drosophila_pd.perturbations import (
    ActionPerturbationContext,
    BrainDrivenPerturbation,
    ControllerPerturbationContext,
)


@dataclass
class Action:
    joint_angles: np.ndarray
    adhesion_onoff: np.ndarray | None = None


def _action_context(count: int = 4) -> ActionPerturbationContext:
    return ActionPerturbationContext(
        condition_id="bridge",
        step_index=0,
        time_s=0.0,
        timestep_s=1e-4,
        random_seed=0,
        expected_joint_angle_count=count,
    )


def test_brain_driven_scales_action_and_preserves_adhesion() -> None:
    perturbation = BrainDrivenPerturbation(
        motor_scale=0.8,
        coupling_scale=0.75,
        name="test_bridge",
    )
    source = Action(np.arange(4, dtype=float), np.array([True, False]))
    transformed = perturbation.apply_to_action(source, _action_context())

    np.testing.assert_allclose(transformed.joint_angles, source.joint_angles * 0.8)
    np.testing.assert_array_equal(transformed.adhesion_onoff, source.adhesion_onoff)
    assert transformed is not source
    assert perturbation.metadata()["deterministic"] is True


def test_brain_driven_loads_json_and_applies_cpg_scale(tmp_path) -> None:
    path = tmp_path / "bridge_scales.json"
    path.write_text(
        json.dumps(
            {
                "model": "example",
                "motor_scale": 0.8,
                "coupling_scale": 0.7,
            }
        ),
        encoding="utf-8",
    )
    perturbation = BrainDrivenPerturbation.from_json(path)
    assert perturbation.model == "example"
    assert perturbation.motor_scale == pytest.approx(0.8)

    class Network:
        coupling_weights = np.ones((2, 2))

    class Controller:
        cpg_network = Network()

    controller = perturbation.apply_to_controller(
        Controller(),
        ControllerPerturbationContext(
            condition_id="bridge",
            timestep_s=1e-4,
            random_seed=0,
            expected_joint_angle_count=4,
        ),
    )
    np.testing.assert_allclose(controller.cpg_network.coupling_weights, 0.7)


def test_brain_driven_rejects_non_finite_scale() -> None:
    with pytest.raises(ValueError, match="finite"):
        BrainDrivenPerturbation(motor_scale=float("nan"))
