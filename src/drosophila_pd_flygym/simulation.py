from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import numpy as np


class SimulationBackend(Protocol):
    def run(self, *, drive_signal: np.ndarray, timestep_s: float) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class SimulationConfig:
    duration_s: float = 2.0
    timestep_s: float = 0.01
    pd_severity: float = 0.0
    baseline_stride_amplitude: float = 1.0
    seed: int | None = 0

    def __post_init__(self) -> None:
        if self.duration_s <= 0:
            raise ValueError("duration_s must be positive")
        if self.timestep_s <= 0:
            raise ValueError("timestep_s must be positive")
        if not 0.0 <= self.pd_severity <= 1.0:
            raise ValueError("pd_severity must be between 0 and 1")
        if self.baseline_stride_amplitude <= 0:
            raise ValueError("baseline_stride_amplitude must be positive")


class DrosophilaPDSimulation:
    def __init__(self, config: SimulationConfig, backend: SimulationBackend | None = None):
        self.config = config
        self.backend = backend

    def build_drive_signal(self) -> np.ndarray:
        num_steps = int(np.ceil(self.config.duration_s / self.config.timestep_s))
        t = np.arange(num_steps, dtype=float) * self.config.timestep_s

        base = self.config.baseline_stride_amplitude * np.sin(2 * np.pi * 6.0 * t)
        left = base.copy()
        right = -base

        severity = self.config.pd_severity
        left *= 1.0 - 0.40 * severity
        right *= 1.0 - 0.60 * severity

        tremor = 0.05 * severity * np.sin(2 * np.pi * 20.0 * t)
        left += tremor
        right += tremor

        return np.column_stack((left, right))

    def run(self) -> dict[str, Any]:
        drive_signal = self.build_drive_signal()

        if self.backend is not None:
            return self.backend.run(
                drive_signal=drive_signal,
                timestep_s=self.config.timestep_s,
            )

        speed_proxy = float(np.mean(np.abs(np.diff(drive_signal, axis=0))))
        asymmetry = float(np.mean(np.abs(drive_signal[:, 0] + drive_signal[:, 1])))

        return {
            "drive_signal": drive_signal,
            "pd_severity": self.config.pd_severity,
            "speed_proxy": speed_proxy,
            "asymmetry": asymmetry,
        }


def make_flygym_backend(*args: Any, **kwargs: Any) -> Any:
    try:
        import flygym  # noqa: F401
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "FlyGym is not installed. Install optional dependency group 'sim' to run backend simulations."
        ) from exc

    raise NotImplementedError(
        "FlyGym/NeuroMechFly/MuJoCo backend wiring depends on the installed FlyGym version. "
        "Provide a backend implementing SimulationBackend.run()."
    )
