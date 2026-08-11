from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from drosophila_pd.perturbations import (  # noqa: E402
    ActionPerturbationContext,
    GlobalActionScalePerturbation,
    IdentityPerturbation,
    load_perturbation_config,
    perturbation_from_mapping,
    perturbation_metadata_complete,
)


@dataclass
class FakeAction:
    joint_angles: np.ndarray
    adhesion_onoff: np.ndarray | None = None


def test_identity_config_parses_and_records_complete_metadata():
    perturbation = load_perturbation_config(
        REPO_ROOT / "configs" / "experiments" / "perturbations" / "identity.yaml"
    )

    assert isinstance(perturbation, IdentityPerturbation)
    assert perturbation.perturbation_type == "identity"
    assert perturbation_metadata_complete(perturbation.metadata())


def test_action_scale_config_parses_scale():
    perturbation = load_perturbation_config(
        REPO_ROOT
        / "configs"
        / "experiments"
        / "perturbations"
        / "action_scale_080.yaml"
    )

    assert isinstance(perturbation, GlobalActionScalePerturbation)
    assert perturbation.scale == 0.8
    assert perturbation.metadata()["intervention_target"] == (
        "controller_joint_angle_commands"
    )


def test_identity_action_transformation_preserves_values():
    action = FakeAction(
        joint_angles=np.array([0.1, -0.2, 0.3]),
        adhesion_onoff=np.array([True, False, True, False, True, False]),
    )

    transformed = IdentityPerturbation().apply_to_action(
        action, _context(expected_joint_angle_count=3)
    )

    assert np.array_equal(transformed.joint_angles, action.joint_angles)
    assert np.array_equal(transformed.adhesion_onoff, action.adhesion_onoff)


def test_global_action_scale_scales_joint_angles_only():
    action = FakeAction(
        joint_angles=np.array([1.0, -2.0, 3.0]),
        adhesion_onoff=np.array([True, False, True, False, True, False]),
    )

    transformed = GlobalActionScalePerturbation(scale=0.8).apply_to_action(
        action, _context(expected_joint_angle_count=3)
    )

    assert np.allclose(transformed.joint_angles, np.array([0.8, -1.6, 2.4]))
    assert np.array_equal(transformed.adhesion_onoff, action.adhesion_onoff)


def test_global_action_scale_is_deterministic():
    action = FakeAction(
        joint_angles=np.linspace(-1.0, 1.0, 42),
        adhesion_onoff=np.array([True, False, True, False, True, False]),
    )
    perturbation = GlobalActionScalePerturbation(scale=0.8)

    first = perturbation.apply_to_action(action, _context())
    second = perturbation.apply_to_action(action, _context())

    assert np.array_equal(first.joint_angles, second.joint_angles)
    assert np.array_equal(first.adhesion_onoff, second.adhesion_onoff)


def test_invalid_scale_values_are_rejected():
    with pytest.raises(ValueError, match="finite and non-negative"):
        GlobalActionScalePerturbation(scale=-0.1)
    with pytest.raises(ValueError, match="finite and non-negative"):
        GlobalActionScalePerturbation(scale=float("nan"))


def test_action_dimension_mismatch_is_rejected():
    action = FakeAction(joint_angles=np.zeros(41))

    with pytest.raises(ValueError, match="expected count"):
        GlobalActionScalePerturbation(scale=0.8).apply_to_action(action, _context())


def test_nested_perturbation_mapping_is_supported():
    perturbation = perturbation_from_mapping(
        {
            "experiment_id": "nested_config",
            "perturbation": {
                "type": "global_action_scale",
                "name": "nested_scale",
                "scale": 0.5,
            },
        }
    )

    assert isinstance(perturbation, GlobalActionScalePerturbation)
    assert perturbation.config_id == "nested_config"


def _context(expected_joint_angle_count: int = 42) -> ActionPerturbationContext:
    return ActionPerturbationContext(
        condition_id="test",
        step_index=0,
        time_s=0.0,
        timestep_s=0.0001,
        random_seed=0,
        expected_joint_angle_count=expected_joint_angle_count,
    )
