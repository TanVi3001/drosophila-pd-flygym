"""Configurable computational motor-control perturbation layer.

The layer sits between an existing healthy controller and the FlyGym action
interface.  It is deliberately a control-level abstraction: FlyGym does not
expose a biological dopaminergic neural network, so these parameters must not
be interpreted as neuron weights or as a validated disease mechanism.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from drosophila_pd.perturbations import (
    ActionPerturbationContext,
    ControllerPerturbationContext,
    CPGCouplingScalePerturbation,
)


COMPUTATIONAL_SCOPE = (
    "A deterministic, control-level perturbation layer for generating and "
    "calibrating simulated locomotor conditions. It is not a biological "
    "Parkinson model, a neural-network model, or clinical validation."
)


@dataclass(frozen=True)
class DiseaseLayer:
    """Apply explicit, seed-controlled motor-control transformations.

    Parameters are generic computational controls. ``motor_vigor`` scales
    joint-angle commands, ``coordination`` scales CPG coupling, and the other
    fields describe optional action-level transformations.  Left/right index
    maps are intentionally supplied by the caller because the mapping is
    model-specific and must not be guessed by this package.
    """

    motor_vigor: float = 1.0
    coordination: float = 1.0
    initiation_delay_steps: int = 0
    motor_noise_std: float = 0.0
    fatigue_rate: float = 0.0
    asymmetry: float = 0.0
    left_joint_indices: tuple[int, ...] = ()
    right_joint_indices: tuple[int, ...] = ()
    random_seed: int = 0
    name: str = "computational_disease_layer"
    config_id: str | None = None

    def __post_init__(self) -> None:
        numeric_fields = {
            "motor_vigor": self.motor_vigor,
            "coordination": self.coordination,
            "motor_noise_std": self.motor_noise_std,
            "fatigue_rate": self.fatigue_rate,
            "asymmetry": self.asymmetry,
        }
        for field_name, value in numeric_fields.items():
            if not np.isfinite(float(value)):
                raise ValueError(f"{field_name} must be finite.")
        if float(self.motor_vigor) < 0:
            raise ValueError("motor_vigor must be non-negative.")
        if float(self.coordination) < 0:
            raise ValueError("coordination must be non-negative.")
        if float(self.motor_noise_std) < 0:
            raise ValueError("motor_noise_std must be non-negative.")
        if float(self.fatigue_rate) < 0:
            raise ValueError("fatigue_rate must be non-negative.")
        if not -1.0 <= float(self.asymmetry) <= 1.0:
            raise ValueError("asymmetry must be between -1 and 1.")
        if int(self.initiation_delay_steps) < 0:
            raise ValueError("initiation_delay_steps must be non-negative.")
        if not str(self.name).strip():
            raise ValueError("name must be a non-empty string.")

        left = tuple(int(index) for index in self.left_joint_indices)
        right = tuple(int(index) for index in self.right_joint_indices)
        if len(set(left)) != len(left) or len(set(right)) != len(right):
            raise ValueError("left_joint_indices and right_joint_indices must be unique.")
        if float(self.asymmetry) != 0.0 and (not left or not right or len(left) != len(right)):
            raise ValueError(
                "non-zero asymmetry requires equally sized left/right joint index maps."
            )
        object.__setattr__(self, "motor_vigor", float(self.motor_vigor))
        object.__setattr__(self, "coordination", float(self.coordination))
        object.__setattr__(self, "initiation_delay_steps", int(self.initiation_delay_steps))
        object.__setattr__(self, "motor_noise_std", float(self.motor_noise_std))
        object.__setattr__(self, "fatigue_rate", float(self.fatigue_rate))
        object.__setattr__(self, "asymmetry", float(self.asymmetry))
        object.__setattr__(self, "left_joint_indices", left)
        object.__setattr__(self, "right_joint_indices", right)
        object.__setattr__(self, "random_seed", int(self.random_seed))
        object.__setattr__(self, "config_id", None if self.config_id is None else str(self.config_id))

    @property
    def perturbation_type(self) -> str:
        """Return the stable perturbation type consumed by the runner."""

        return "disease_layer"

    def apply_to_config(self, config: Any) -> Any:
        """Leave the simulation configuration unchanged."""

        return config

    def apply_to_controller(
        self, controller: Any, context: ControllerPerturbationContext
    ) -> Any:
        """Apply only the declared CPG coordination transformation."""

        if self.coordination == 1.0:
            return controller
        return CPGCouplingScalePerturbation(
            scale=self.coordination,
            name=f"{self.name}_coordination",
            config_id=self.config_id,
        ).apply_to_controller(controller, context)

    def apply_to_action(self, action: Any, context: ActionPerturbationContext) -> Any:
        """Transform one action using a reproducible computational recipe."""

        joint_angles = np.asarray(action.joint_angles, dtype=float)
        if joint_angles.ndim != 1:
            raise ValueError("Locomotion joint-angle commands must be one-dimensional.")
        if int(context.expected_joint_angle_count) > 0 and (
            joint_angles.shape[0] != int(context.expected_joint_angle_count)
        ):
            raise ValueError("Locomotion joint-angle command count does not match expected count.")
        if not np.isfinite(joint_angles).all():
            raise ValueError("Locomotion joint-angle commands must be finite.")

        transformed = joint_angles.copy()
        fatigue_factor = max(0.0, 1.0 - self.fatigue_rate * float(context.time_s))
        transformed *= self.motor_vigor * fatigue_factor
        if context.step_index < self.initiation_delay_steps:
            transformed.fill(0.0)

        if self.asymmetry != 0.0:
            for left_index, right_index in zip(
                self.left_joint_indices, self.right_joint_indices
            ):
                if left_index >= transformed.size or right_index >= transformed.size:
                    raise ValueError("Asymmetry joint index exceeds action dimensions.")
                transformed[left_index] *= 1.0 + self.asymmetry
                transformed[right_index] *= 1.0 - self.asymmetry

        if self.motor_noise_std != 0.0:
            rng = np.random.default_rng(
                np.random.SeedSequence(
                    [self.random_seed, int(context.random_seed), int(context.step_index)]
                )
            )
            transformed += rng.normal(0.0, self.motor_noise_std, size=transformed.shape)

        adhesion = getattr(action, "adhesion_onoff", None)
        copied_adhesion = None if adhesion is None else np.asarray(adhesion, dtype=bool).copy()
        return type(action)(joint_angles=transformed, adhesion_onoff=copied_adhesion)

    def metadata(self) -> dict[str, Any]:
        """Return auditable, JSON-serializable layer metadata."""

        return {
            "type": self.perturbation_type,
            "name": self.name,
            "config_id": self.config_id,
            "parameters": {
                "motor_vigor": self.motor_vigor,
                "coordination": self.coordination,
                "initiation_delay_steps": self.initiation_delay_steps,
                "motor_noise_std": self.motor_noise_std,
                "fatigue_rate": self.fatigue_rate,
                "asymmetry": self.asymmetry,
                "left_joint_indices": list(self.left_joint_indices),
                "right_joint_indices": list(self.right_joint_indices),
                "random_seed": self.random_seed,
            },
            "intervention_target": "controller_and_joint_angle_action",
            "intervention_stage": "controller_and_post_controller_pre_simulation_action",
            "deterministic": True,
            "action_validation": "structural_only_for_custom_transforms",
            "scientific_scope": COMPUTATIONAL_SCOPE,
            "description": (
                "Generic computational Disease Layer. Parameters are control-level "
                "proxies and require external literature targets before calibration."
            ),
        }

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "DiseaseLayer":
        """Build a validated layer from a YAML/JSON-compatible mapping."""

        values = dict(data)
        if isinstance(values.get("disease_layer"), dict):
            nested = dict(values["disease_layer"])
            for key in ("name", "config_id", "experiment_id"):
                if key in values and key not in nested:
                    nested[key] = values[key]
            values = nested
        if "experiment_id" in values and "config_id" not in values:
            values["config_id"] = values.pop("experiment_id")
        for key in ("left_joint_indices", "right_joint_indices"):
            if key in values:
                if not isinstance(values[key], (list, tuple)):
                    raise ValueError(f"{key} must be a list of integer indices.")
                values[key] = tuple(int(index) for index in values[key])
        allowed = {
            "motor_vigor",
            "coordination",
            "initiation_delay_steps",
            "motor_noise_std",
            "fatigue_rate",
            "asymmetry",
            "left_joint_indices",
            "right_joint_indices",
            "random_seed",
            "name",
            "config_id",
        }
        unknown = sorted(set(values) - allowed)
        if unknown:
            raise ValueError(f"Unsupported Disease Layer fields: {unknown}")
        return cls(**values)


__all__ = ["COMPUTATIONAL_SCOPE", "DiseaseLayer"]
