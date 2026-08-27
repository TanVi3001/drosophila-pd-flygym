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
    _copy_action,
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
    action_latency_steps: int = 0
    freezing_probability: float = 0.0
    freezing_duration_steps: int = 0
    left_joint_gains: tuple[float, ...] = ()
    right_joint_gains: tuple[float, ...] = ()
    left_joint_offsets: tuple[float, ...] = ()
    right_joint_offsets: tuple[float, ...] = ()

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
        if int(self.action_latency_steps) < 0:
            raise ValueError("action_latency_steps must be non-negative.")
        if not 0.0 <= float(self.freezing_probability) <= 1.0:
            raise ValueError("freezing_probability must be between 0 and 1.")
        if int(self.freezing_duration_steps) < 0:
            raise ValueError("freezing_duration_steps must be non-negative.")
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
        if set(left) & set(right):
            raise ValueError("left_joint_indices and right_joint_indices must be disjoint.")
        vector_values = {
            "left_joint_gains": self.left_joint_gains,
            "right_joint_gains": self.right_joint_gains,
            "left_joint_offsets": self.left_joint_offsets,
            "right_joint_offsets": self.right_joint_offsets,
        }
        vectors: dict[str, tuple[float, ...]] = {}
        for field_name, values in vector_values.items():
            vector = tuple(float(value) for value in values)
            if any(not np.isfinite(value) for value in vector):
                raise ValueError(f"{field_name} must contain only finite values.")
            if vector and (not left or len(vector) != len(left)):
                raise ValueError(
                    f"{field_name} must match the left/right joint index map length."
                )
            vectors[field_name] = vector
        if vectors["left_joint_gains"] and not vectors["right_joint_gains"]:
            raise ValueError("left_joint_gains requires right_joint_gains.")
        if vectors["right_joint_gains"] and not vectors["left_joint_gains"]:
            raise ValueError("right_joint_gains requires left_joint_gains.")
        if vectors["left_joint_offsets"] and not vectors["right_joint_offsets"]:
            raise ValueError("left_joint_offsets requires right_joint_offsets.")
        if vectors["right_joint_offsets"] and not vectors["left_joint_offsets"]:
            raise ValueError("right_joint_offsets requires left_joint_offsets.")
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
        object.__setattr__(self, "action_latency_steps", int(self.action_latency_steps))
        object.__setattr__(self, "freezing_probability", float(self.freezing_probability))
        object.__setattr__(self, "freezing_duration_steps", int(self.freezing_duration_steps))
        # Cache the deterministic freeze state as frames are requested.  The
        # cache changes only execution cost, not the seed-controlled sequence;
        # without it, each frame would replay the complete history from step 0.
        object.__setattr__(self, "_freezing_cache", {})
        for field_name, values in vectors.items():
            object.__setattr__(self, field_name, values)

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

        source_adhesion = getattr(action, "adhesion_onoff", None)
        if self.action_latency_steps:
            history = tuple(context.action_history)
            if len(history) >= self.action_latency_steps:
                delayed_action = history[-self.action_latency_steps]
                transformed = np.asarray(delayed_action.joint_angles, dtype=float).copy()
                source_adhesion = getattr(delayed_action, "adhesion_onoff", source_adhesion)
                if transformed.shape != joint_angles.shape or not np.isfinite(transformed).all():
                    raise ValueError("Delayed action does not match the current action shape.")
            else:
                transformed = np.zeros_like(joint_angles)
        else:
            transformed = joint_angles.copy()
        fatigue_factor = max(0.0, 1.0 - self.fatigue_rate * float(context.time_s))
        transformed *= self.motor_vigor * fatigue_factor
        if context.step_index < self.initiation_delay_steps:
            transformed.fill(0.0)

        if self.asymmetry != 0.0 or self.left_joint_gains or self.left_joint_offsets:
            for pair_index, (left_index, right_index) in enumerate(
                zip(self.left_joint_indices, self.right_joint_indices)
            ):
                if left_index >= transformed.size or right_index >= transformed.size:
                    raise ValueError("Asymmetry joint index exceeds action dimensions.")
                left_gain = (
                    self.left_joint_gains[pair_index]
                    if self.left_joint_gains
                    else 1.0 + self.asymmetry
                )
                right_gain = (
                    self.right_joint_gains[pair_index]
                    if self.right_joint_gains
                    else 1.0 - self.asymmetry
                )
                left_offset = self.left_joint_offsets[pair_index] if self.left_joint_offsets else 0.0
                right_offset = self.right_joint_offsets[pair_index] if self.right_joint_offsets else 0.0
                transformed[left_index] = transformed[left_index] * left_gain + left_offset
                transformed[right_index] = transformed[right_index] * right_gain + right_offset

        if self.motor_noise_std != 0.0:
            rng = np.random.default_rng(
                np.random.SeedSequence(
                    [self.random_seed, int(context.random_seed), int(context.step_index)]
                )
            )
            transformed += rng.normal(0.0, self.motor_noise_std, size=transformed.shape)

        if self._freezing_active(context):
            transformed.fill(0.0)

        return _copy_action(action, joint_angles=transformed, adhesion_onoff=source_adhesion)

    def _freezing_active(self, context: ActionPerturbationContext) -> bool:
        """Return the seed-controlled freeze state at one action step."""

        if self.freezing_probability <= 0.0 or self.freezing_duration_steps <= 0:
            return False
        target = int(context.step_index)
        if target < 0:
            return False

        cache_key = int(context.random_seed)
        cache = self._freezing_cache.setdefault(
            cache_key,
            {"states": [], "remaining": 0},
        )
        states = cache["states"]
        remaining = int(cache["remaining"])
        for step_index in range(len(states), target + 1):
            if remaining > 0:
                active = True
                remaining -= 1
            else:
                rng = np.random.default_rng(
                    np.random.SeedSequence(
                        [self.random_seed, cache_key, step_index, 193]
                    )
                )
                active = bool(rng.random() < self.freezing_probability)
                remaining = self.freezing_duration_steps - 1 if active else 0
            states.append(active)
        cache["remaining"] = remaining
        return bool(states[target])

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
                "action_latency_steps": self.action_latency_steps,
                "freezing_probability": self.freezing_probability,
                "freezing_duration_steps": self.freezing_duration_steps,
                "left_joint_indices": list(self.left_joint_indices),
                "right_joint_indices": list(self.right_joint_indices),
                "left_joint_gains": list(self.left_joint_gains),
                "right_joint_gains": list(self.right_joint_gains),
                "left_joint_offsets": list(self.left_joint_offsets),
                "right_joint_offsets": list(self.right_joint_offsets),
                "random_seed": self.random_seed,
            },
            "intervention_target": "controller_and_joint_angle_action",
            "intervention_stage": "controller_and_post_controller_pre_simulation_action",
            "deterministic": True,
            "action_validation": "structural_only_for_custom_transforms",
            "scientific_scope": COMPUTATIONAL_SCOPE,
            "unsupported_proxies": {
                "postural_instability": {
                    "status": "UNSUPPORTED",
                    "reason": (
                        "LocomotionAction exposes joint_angles and adhesion_onoff, "
                        "but no orientation or body-stabilization command."
                    ),
                }
            },
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
        if "experiment_id" in values:
            # ``experiment_id`` is the historical config alias.  Preserve an
            # explicit ``config_id`` when both are present, but never pass the
            # alias through to the dataclass constructor as an unknown field.
            experiment_id = values.pop("experiment_id")
            values.setdefault("config_id", experiment_id)
        if "latency_steps" in values:
            # Keep the short historical alias accepted, while preferring the
            # explicit field when a mapping contains both spellings.
            latency_steps = values.pop("latency_steps")
            values.setdefault("action_latency_steps", latency_steps)
        for key in ("left_joint_indices", "right_joint_indices"):
            if key in values:
                if not isinstance(values[key], (list, tuple)):
                    raise ValueError(f"{key} must be a list of integer indices.")
                values[key] = tuple(int(index) for index in values[key])
        for key in (
            "left_joint_gains",
            "right_joint_gains",
            "left_joint_offsets",
            "right_joint_offsets",
        ):
            if key in values:
                if not isinstance(values[key], (list, tuple)):
                    raise ValueError(f"{key} must be a list of numeric values.")
                values[key] = tuple(float(value) for value in values[key])
        allowed = {
            "motor_vigor",
            "coordination",
            "initiation_delay_steps",
            "motor_noise_std",
            "fatigue_rate",
            "asymmetry",
            "left_joint_indices",
            "right_joint_indices",
            "action_latency_steps",
            "freezing_probability",
            "freezing_duration_steps",
            "left_joint_gains",
            "right_joint_gains",
            "left_joint_offsets",
            "right_joint_offsets",
            "random_seed",
            "name",
            "config_id",
        }
        unknown = sorted(set(values) - allowed)
        if unknown:
            raise ValueError(f"Unsupported Disease Layer fields: {unknown}")
        return cls(**values)


__all__ = ["COMPUTATIONAL_SCOPE", "DiseaseLayer"]
