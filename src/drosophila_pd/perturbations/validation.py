"""Validation summaries for perturbation action transformations."""

from __future__ import annotations

import math
from typing import Any

import numpy as np


def summarize_action_transformation(
    *,
    controller_joint_angle_actions: np.ndarray,
    applied_joint_angle_actions: np.ndarray,
    controller_adhesion_onoff: np.ndarray | None,
    applied_adhesion_onoff: np.ndarray | None,
    expected_joint_angle_count: int,
    perturbation_metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    """Summarize whether applied actions match the declared perturbation."""

    controller_actions = np.asarray(controller_joint_angle_actions, dtype=float)
    applied_actions = np.asarray(applied_joint_angle_actions, dtype=float)
    action_dimensions_valid = (
        controller_actions.ndim == 2
        and applied_actions.ndim == 2
        and controller_actions.shape == applied_actions.shape
        and controller_actions.shape[1] == expected_joint_angle_count
    )
    adhesion_preserved = _adhesion_preserved(
        controller_adhesion_onoff, applied_adhesion_onoff
    )
    metadata_type = (
        perturbation_metadata.get("type") if perturbation_metadata is not None else None
    )
    scale = None
    expected_actions = controller_actions
    expected_transform = "identity"
    if metadata_type == "global_action_scale":
        scale = float(perturbation_metadata["parameters"]["scale"])
        expected_actions = controller_actions * scale
        expected_transform = "global_action_scale"

    transform_error = (
        _max_abs_difference(expected_actions, applied_actions)
        if action_dimensions_valid
        else None
    )
    transform_pass = (
        transform_error is not None
        and transform_error <= 1e-12
        and action_dimensions_valid
    )
    return {
        "perturbation_type": metadata_type,
        "expected_transform": expected_transform,
        "expected_scale": scale,
        "controller_joint_angle_shape": [int(value) for value in controller_actions.shape],
        "applied_joint_angle_shape": [int(value) for value in applied_actions.shape],
        "expected_joint_angle_count": int(expected_joint_angle_count),
        "action_dimensions_valid": action_dimensions_valid,
        "adhesion_commands_preserved": adhesion_preserved,
        "joint_angle_transform_error_max": _json_float(transform_error),
        "joint_angle_transform_check": _check(True, transform_pass),
        "structural_checks": {
            "action_dimensions_valid": _check(True, action_dimensions_valid),
            "adhesion_commands_preserved": _check(True, adhesion_preserved),
            "joint_angle_transform_matches_expected": _check(True, transform_pass),
        },
    }


def _adhesion_preserved(
    controller_adhesion_onoff: np.ndarray | None,
    applied_adhesion_onoff: np.ndarray | None,
) -> bool:
    if controller_adhesion_onoff is None and applied_adhesion_onoff is None:
        return True
    if controller_adhesion_onoff is None or applied_adhesion_onoff is None:
        return False
    controller = np.asarray(controller_adhesion_onoff, dtype=bool)
    applied = np.asarray(applied_adhesion_onoff, dtype=bool)
    return controller.shape == applied.shape and bool(np.array_equal(controller, applied))


def _max_abs_difference(left: np.ndarray, right: np.ndarray) -> float | None:
    if left.shape != right.shape or left.size == 0:
        return None
    difference = np.abs(left - right)
    if not np.isfinite(difference).all():
        return None
    return float(np.max(difference))


def _check(expected: Any, observed: Any) -> dict[str, Any]:
    return {
        "expected": expected,
        "observed": observed,
        "pass": observed == expected,
    }


def _json_float(value: Any) -> float | None:
    try:
        as_float = float(value)
    except (TypeError, ValueError):
        return None
    return as_float if math.isfinite(as_float) else None


__all__ = ["summarize_action_transformation"]
