"""Explicit perturbation interfaces for paired simulation experiments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import numpy as np
import yaml


@dataclass(frozen=True)
class ControllerPerturbationContext:
    """Context available before a controller is used for a rollout."""

    condition_id: str
    timestep_s: float
    random_seed: int
    expected_joint_angle_count: int


@dataclass(frozen=True)
class ActionPerturbationContext:
    """Context available when transforming one controller action."""

    condition_id: str
    step_index: int
    time_s: float
    timestep_s: float
    random_seed: int
    expected_joint_angle_count: int


class Perturbation(Protocol):
    """Small protocol implemented by deterministic perturbations."""

    @property
    def perturbation_type(self) -> str:
        """Stable machine-readable perturbation type."""

    @property
    def name(self) -> str:
        """Stable run/config name."""

    def apply_to_config(self, config: Any) -> Any:
        """Return the config used for the perturbed condition."""

    def apply_to_controller(
        self, controller: Any, context: ControllerPerturbationContext
    ) -> Any:
        """Return the controller used for the perturbed condition."""

    def apply_to_action(self, action: Any, context: ActionPerturbationContext) -> Any:
        """Return the action sent to the simulation."""

    def metadata(self) -> dict[str, Any]:
        """Return JSON-serializable perturbation metadata."""


@dataclass(frozen=True)
class IdentityPerturbation:
    """A perturbation that deliberately changes no simulation command."""

    name: str = "identity"
    config_id: str | None = None

    @property
    def perturbation_type(self) -> str:
        return "identity"

    def apply_to_config(self, config: Any) -> Any:
        return config

    def apply_to_controller(
        self, controller: Any, context: ControllerPerturbationContext
    ) -> Any:
        return controller

    def apply_to_action(self, action: Any, context: ActionPerturbationContext) -> Any:
        _validate_joint_angles(action.joint_angles, context.expected_joint_angle_count)
        return _copy_action(action)

    def metadata(self) -> dict[str, Any]:
        return {
            "type": self.perturbation_type,
            "name": self.name,
            "config_id": self.config_id,
            "parameters": {},
            "intervention_target": "none",
            "intervention_stage": "none",
            "deterministic": True,
            "description": (
                "Identity validation perturbation. It must not change controller "
                "commands, adhesion commands, configuration, or controller state."
            ),
        }


NoOpPerturbation = IdentityPerturbation


@dataclass(frozen=True)
class GlobalActionScalePerturbation:
    """Scale only joint-angle commands after controller output."""

    scale: float = 0.8
    name: str = "action_scale_080"
    config_id: str | None = None

    def __post_init__(self) -> None:
        scale = float(self.scale)
        if not np.isfinite(scale) or scale < 0:
            raise ValueError("global_action_scale.scale must be finite and non-negative.")
        object.__setattr__(self, "scale", scale)

    @property
    def perturbation_type(self) -> str:
        return "global_action_scale"

    def apply_to_config(self, config: Any) -> Any:
        return config

    def apply_to_controller(
        self, controller: Any, context: ControllerPerturbationContext
    ) -> Any:
        return controller

    def apply_to_action(self, action: Any, context: ActionPerturbationContext) -> Any:
        joint_angles = _validate_joint_angles(
            action.joint_angles, context.expected_joint_angle_count
        )
        return _copy_action(action, joint_angles=joint_angles * self.scale)

    def metadata(self) -> dict[str, Any]:
        return {
            "type": self.perturbation_type,
            "name": self.name,
            "config_id": self.config_id,
            "parameters": {"scale": self.scale},
            "intervention_target": "controller_joint_angle_commands",
            "intervention_stage": "post_controller_pre_simulation_action",
            "deterministic": True,
            "description": (
                "Generic motor-command perturbation that scales the joint-angle "
                "portion of each controller action. Adhesion commands are not scaled."
            ),
        }


def load_perturbation_config(path: str | Path) -> Perturbation:
    """Load a perturbation from a YAML config file."""

    with Path(path).open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError("Perturbation configuration root must be a mapping.")
    return perturbation_from_mapping(loaded)


def perturbation_from_mapping(data: dict[str, Any]) -> Perturbation:
    """Build a supported perturbation from a mapping."""

    values = _normalise_perturbation_mapping(data)
    perturbation_type = str(values.get("type", "identity")).strip().lower()
    name = str(values.get("name", perturbation_type)).strip()
    if not name:
        raise ValueError("Perturbation name must be a non-empty string.")
    config_id = values.get("experiment_id") or values.get("config_id")
    config_id = str(config_id) if config_id is not None else None

    if perturbation_type in {"identity", "noop", "no_op"}:
        return IdentityPerturbation(name=name, config_id=config_id)
    if perturbation_type == "global_action_scale":
        if "scale" not in values:
            raise ValueError("global_action_scale perturbation requires scale.")
        return GlobalActionScalePerturbation(
            scale=float(values["scale"]),
            name=name,
            config_id=config_id,
        )
    raise ValueError(f"Unsupported perturbation type: {perturbation_type}")


def perturbation_metadata_complete(metadata: dict[str, Any]) -> bool:
    """Return whether required metadata fields are present and usable."""

    required = (
        "type",
        "name",
        "parameters",
        "intervention_target",
        "intervention_stage",
        "deterministic",
    )
    if any(key not in metadata for key in required):
        return False
    return (
        isinstance(metadata["type"], str)
        and bool(metadata["type"].strip())
        and isinstance(metadata["name"], str)
        and bool(metadata["name"].strip())
        and isinstance(metadata["parameters"], dict)
        and isinstance(metadata["intervention_target"], str)
        and bool(metadata["intervention_target"].strip())
        and isinstance(metadata["intervention_stage"], str)
        and bool(metadata["intervention_stage"].strip())
        and metadata["deterministic"] is True
    )


def _normalise_perturbation_mapping(data: dict[str, Any]) -> dict[str, Any]:
    root = dict(data)
    if isinstance(root.get("perturbation"), dict):
        nested = dict(root["perturbation"])
        for key in ("experiment_id", "config_id", "name"):
            if key in root and key not in nested:
                nested[key] = root[key]
        return nested
    return root


def _validate_joint_angles(values: Any, expected_count: int) -> np.ndarray:
    joint_angles = np.asarray(values, dtype=float)
    if joint_angles.ndim != 1:
        raise ValueError("Locomotion joint-angle commands must be one-dimensional.")
    if int(expected_count) > 0 and joint_angles.shape[0] != int(expected_count):
        raise ValueError(
            "Locomotion joint-angle command count does not match expected count."
        )
    if not np.isfinite(joint_angles).all():
        raise ValueError("Locomotion joint-angle commands must be finite.")
    return joint_angles


_UNCHANGED = object()


def _copy_action(
    action: Any,
    *,
    joint_angles: Any | None = None,
    adhesion_onoff: Any = _UNCHANGED,
) -> Any:
    action_type = type(action)
    copied_joint_angles = (
        np.asarray(action.joint_angles, dtype=float).copy()
        if joint_angles is None
        else np.asarray(joint_angles, dtype=float).copy()
    )
    if adhesion_onoff is _UNCHANGED:
        source_adhesion = action.adhesion_onoff
    else:
        source_adhesion = adhesion_onoff
    copied_adhesion = (
        None
        if source_adhesion is None
        else np.asarray(source_adhesion, dtype=bool).copy()
    )
    return action_type(
        joint_angles=copied_joint_angles,
        adhesion_onoff=copied_adhesion,
    )


__all__ = [
    "ActionPerturbationContext",
    "ControllerPerturbationContext",
    "GlobalActionScalePerturbation",
    "IdentityPerturbation",
    "NoOpPerturbation",
    "Perturbation",
    "load_perturbation_config",
    "perturbation_from_mapping",
    "perturbation_metadata_complete",
]
