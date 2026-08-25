"""Unit tests for action-level Disease Layer proxies without simulation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pytest

from drosophila_pd.parkinson import DiseaseLayer
from drosophila_pd.perturbations import ActionPerturbationContext, load_perturbation_config


@dataclass
class _Action:
    joint_angles: np.ndarray
    adhesion_onoff: np.ndarray | None = None


def _context(
    step: int,
    *,
    history: tuple[_Action, ...] = (),
    seed: int = 11,
) -> ActionPerturbationContext:
    return ActionPerturbationContext(
        condition_id="proxy_test",
        step_index=step,
        time_s=step * 0.1,
        timestep_s=0.1,
        random_seed=seed,
        expected_joint_angle_count=2,
        action_history=history,
    )


def test_latency_buffers_previous_action_and_preserves_determinism():
    layer = DiseaseLayer(action_latency_steps=1)
    first = _Action(np.array([1.0, 2.0]), np.array([True, False]))
    second = _Action(np.array([3.0, 4.0]), np.array([False, True]))

    startup = layer.apply_to_action(first, _context(0))
    delayed = layer.apply_to_action(second, _context(1, history=(first,)))
    replay = layer.apply_to_action(second, _context(1, history=(first,)))

    assert np.array_equal(startup.joint_angles, [0.0, 0.0])
    assert np.array_equal(delayed.joint_angles, first.joint_angles)
    assert np.array_equal(delayed.adhesion_onoff, first.adhesion_onoff)
    assert np.array_equal(delayed.joint_angles, replay.joint_angles)


def test_freezing_suppresses_actions_with_seed_controlled_probability():
    action = _Action(np.array([1.0, -2.0]), np.array([True, False]))
    always_frozen = DiseaseLayer(
        freezing_probability=1.0,
        freezing_duration_steps=2,
        random_seed=5,
    )
    first = always_frozen.apply_to_action(action, _context(0))
    second = always_frozen.apply_to_action(action, _context(1))
    replay = always_frozen.apply_to_action(action, _context(1))

    assert np.array_equal(first.joint_angles, [0.0, 0.0])
    assert np.array_equal(second.joint_angles, [0.0, 0.0])
    assert np.array_equal(second.joint_angles, replay.joint_angles)
    assert np.array_equal(second.adhesion_onoff, action.adhesion_onoff)
    assert np.array_equal(
        DiseaseLayer(freezing_probability=0.0).apply_to_action(action, _context(0)).joint_angles,
        action.joint_angles,
    )


def test_asymmetry_supports_explicit_left_right_gains_and_offsets():
    layer = DiseaseLayer(
        left_joint_indices=(0,),
        right_joint_indices=(1,),
        left_joint_gains=(2.0,),
        right_joint_gains=(0.5,),
        left_joint_offsets=(0.1,),
        right_joint_offsets=(-0.2,),
    )
    result = layer.apply_to_action(
        _Action(np.array([1.0, 2.0])),
        _context(0),
    )

    assert np.allclose(result.joint_angles, [2.1, 0.8])
    assert layer.metadata()["parameters"]["left_joint_offsets"] == [0.1]


def test_existing_asymmetry_parameter_remains_backward_compatible():
    layer = DiseaseLayer(
        asymmetry=0.25,
        left_joint_indices=(0,),
        right_joint_indices=(1,),
    )
    result = layer.apply_to_action(_Action(np.array([2.0, 2.0])), _context(0))
    assert np.allclose(result.joint_angles, [2.5, 1.5])


def test_action_proxy_config_loads_and_postural_instability_is_explicitly_unsupported():
    config = load_perturbation_config("configs/experiments/disease_layer_action_proxies.yaml")
    assert isinstance(config, DiseaseLayer)
    assert config.action_latency_steps == 3
    assert config.freezing_duration_steps == 20
    assert config.left_joint_gains == (1.05, 1.05)
    assert config.metadata()["unsupported_proxies"]["postural_instability"]["status"] == "UNSUPPORTED"
    with pytest.raises(ValueError, match="Unsupported Disease Layer fields"):
        DiseaseLayer.from_mapping({"postural_instability": 0.2})
