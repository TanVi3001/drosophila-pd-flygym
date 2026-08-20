"""Optimizer interfaces kept separate from calibration execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Protocol

from .parameter_space import ParameterSpace


CandidateScorer = Callable[[Mapping[str, Any]], float]


@dataclass(frozen=True)
class OptimizerResult:
    method: str
    status: str
    best_parameters: dict[str, Any] | None
    best_loss: float | None
    evaluations: tuple[dict[str, Any], ...]

    def to_mapping(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "status": self.status,
            "best_parameters": self.best_parameters,
            "best_loss": self.best_loss,
            "evaluations": [dict(item) for item in self.evaluations],
        }


class Optimizer(Protocol):
    """Protocol for future Grid/Random/Bayesian/Optuna/CMA-ES/SciPy backends."""

    name: str

    def optimize(
        self,
        space: ParameterSpace,
        scorer: CandidateScorer,
    ) -> OptimizerResult:
        ...


class GridSearchOptimizer:
    """Explicit, dependency-free grid search for finite parameter spaces."""

    name = "grid_search"

    def optimize(self, space: ParameterSpace, scorer: CandidateScorer) -> OptimizerResult:
        evaluations: list[dict[str, Any]] = []
        for parameters in space.grid():
            try:
                loss = float(scorer(parameters))
            except Exception as error:  # noqa: BLE001 - retain candidate failure
                evaluations.append(
                    {"parameters": dict(parameters), "status": "FAILED", "error": str(error)}
                )
            else:
                evaluations.append({"parameters": dict(parameters), "status": "PASS", "loss": loss})
        passed = [item for item in evaluations if item["status"] == "PASS"]
        best = min(passed, key=lambda item: item["loss"]) if passed else None
        return OptimizerResult(
            method=self.name,
            status="PASS" if best else "FAILED_NO_CANDIDATE",
            best_parameters=None if best is None else dict(best["parameters"]),
            best_loss=None if best is None else float(best["loss"]),
            evaluations=tuple(evaluations),
        )


_FUTURE_OPTIMIZERS = ("random_search", "bayesian", "optuna", "cma_es", "scipy")


def available_optimizers() -> dict[str, str]:
    """Describe implemented and intentionally deferred optimizer backends."""

    return {
        "grid_search": "available",
        **{name: "interface_only" for name in _FUTURE_OPTIMIZERS},
    }


__all__ = [
    "CandidateScorer",
    "GridSearchOptimizer",
    "Optimizer",
    "OptimizerResult",
    "available_optimizers",
]
