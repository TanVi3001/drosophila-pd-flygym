"""Transparent objective functions for metric-to-literature comparison."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Iterable, Mapping

from drosophila_pd.parkinson.phenotype_database import PhenotypeTarget


SUPPORTED_OBJECTIVES = ("weighted_mse", "weighted_mae", "huber", "cosine")


@dataclass(frozen=True)
class ObjectiveContribution:
    metric: str
    target_id: str
    observed: float
    target: float
    normalized_error: float
    weight: float
    contribution: float

    def to_mapping(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "target_id": self.target_id,
            "observed": self.observed,
            "target": self.target,
            "normalized_error": self.normalized_error,
            "weight": self.weight,
            "contribution": self.contribution,
        }


@dataclass(frozen=True)
class ObjectiveResult:
    """One objective evaluation, including missing-value accounting."""

    method: str
    status: str
    loss: float | None
    available_metrics: tuple[str, ...]
    missing_metrics: tuple[str, ...]
    contributions: tuple[ObjectiveContribution, ...]

    def to_mapping(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "status": self.status,
            "loss": self.loss,
            "available_metrics": list(self.available_metrics),
            "missing_metrics": list(self.missing_metrics),
            "contributions": [item.to_mapping() for item in self.contributions],
        }


@dataclass(frozen=True)
class ObjectiveFunction:
    """Configurable loss function with explicit normalization semantics."""

    method: str = "weighted_mse"
    normalize: bool = True
    missing_policy: str = "ignore"
    huber_delta: float = 1.0

    def __post_init__(self) -> None:
        if self.method not in SUPPORTED_OBJECTIVES:
            raise ValueError(f"method must be one of {SUPPORTED_OBJECTIVES}.")
        if self.missing_policy not in {"ignore", "fail"}:
            raise ValueError("missing_policy must be 'ignore' or 'fail'.")
        if not math.isfinite(float(self.huber_delta)) or self.huber_delta <= 0:
            raise ValueError("huber_delta must be finite and positive.")

    def evaluate(
        self,
        observed: Mapping[str, Any],
        targets: Iterable[PhenotypeTarget],
    ) -> ObjectiveResult:
        target_list = tuple(target for target in targets if target.numeric)
        contributions: list[ObjectiveContribution] = []
        missing: list[str] = []
        for target in target_list:
            observed_value = _finite_float(observed.get(target.metric))
            target_value = _target_center(target)
            if observed_value is None or target_value is None:
                missing.append(target.metric)
                continue
            scale = _target_scale(target) if self.normalize else 1.0
            error = _target_error(observed_value, target, scale)
            contributions.append(
                ObjectiveContribution(
                    metric=target.metric,
                    target_id=target.target_id,
                    observed=observed_value,
                    target=target_value,
                    normalized_error=error,
                    weight=float(target.weight),
                    contribution=0.0,
                )
            )

        if not target_list:
            return ObjectiveResult(
                method=self.method,
                status="UNAVAILABLE_NUMERIC_TARGET",
                loss=None,
                available_metrics=(),
                missing_metrics=(),
                contributions=(),
            )
        if self.missing_policy == "fail" and missing:
            return ObjectiveResult(
                method=self.method,
                status="MISSING_METRICS",
                loss=None,
                available_metrics=tuple(item.metric for item in contributions),
                missing_metrics=tuple(missing),
                contributions=tuple(contributions),
            )
        if not contributions:
            return ObjectiveResult(
                method=self.method,
                status="UNAVAILABLE_METRICS",
                loss=None,
                available_metrics=(),
                missing_metrics=tuple(missing),
                contributions=(),
            )

        if self.method == "cosine":
            # The cosine objective compares observed and target vectors after
            # scaling. A per-metric row retains the same aggregate loss for
            # transparent reporting without pretending it is independent.
            observed_vector = [item.observed / (_target_scale_by_values(item) if self.normalize else 1.0) for item in contributions]
            target_vector = [item.target / (_target_scale_by_values(item) if self.normalize else 1.0) for item in contributions]
            loss = _cosine_distance(observed_vector, target_vector)
            per_item = loss / len(contributions)
        else:
            raw = [_point_loss(item.normalized_error, self.method, self.huber_delta) for item in contributions]
            total_weight = sum(item.weight for item in contributions)
            loss = sum(item.weight * point for item, point in zip(contributions, raw)) / total_weight
            per_item = None

        enriched = tuple(
            ObjectiveContribution(
                metric=item.metric,
                target_id=item.target_id,
                observed=item.observed,
                target=item.target,
                normalized_error=item.normalized_error,
                weight=item.weight,
                contribution=(per_item if per_item is not None else _point_loss(item.normalized_error, self.method, self.huber_delta)),
            )
            for item in contributions
        )
        status = "PASS" if not missing else "PARTIAL"
        return ObjectiveResult(
            method=self.method,
            status=status,
            loss=float(loss),
            available_metrics=tuple(item.metric for item in enriched),
            missing_metrics=tuple(missing),
            contributions=enriched,
        )


def compute_loss(
    observed: Mapping[str, Any],
    targets: Iterable[PhenotypeTarget],
    *,
    method: str = "weighted_mse",
    normalize: bool = True,
    missing_policy: str = "ignore",
    huber_delta: float = 1.0,
) -> ObjectiveResult:
    """Convenience wrapper around :class:`ObjectiveFunction`."""

    return ObjectiveFunction(
        method=method,
        normalize=normalize,
        missing_policy=missing_policy,
        huber_delta=huber_delta,
    ).evaluate(observed, targets)


def _point_loss(error: float, method: str, huber_delta: float) -> float:
    absolute = abs(error)
    if method == "weighted_mse":
        return error * error
    if method == "weighted_mae":
        return absolute
    if method == "huber":
        if absolute <= huber_delta:
            return 0.5 * error * error
        return huber_delta * (absolute - 0.5 * huber_delta)
    raise ValueError(f"Point loss is not defined for {method!r}.")


def _target_center(target: PhenotypeTarget) -> float | None:
    if target.target_value is not None:
        return float(target.target_value)
    if target.target_range is not None:
        return (float(target.target_range[0]) + float(target.target_range[1])) / 2.0
    return None


def _target_scale(target: PhenotypeTarget) -> float:
    if target.scale is not None:
        return float(target.scale)
    center = _target_center(target)
    if center is None:
        return 1.0
    return max(abs(center), 1.0)


def _target_error(observed: float, target: PhenotypeTarget, scale: float) -> float:
    if target.target_range is not None:
        lower, upper = target.target_range
        if lower <= observed <= upper:
            return 0.0
        distance = min(abs(observed - lower), abs(observed - upper))
        return distance / scale
    center = _target_center(target)
    assert center is not None
    return (observed - center) / scale


def _target_scale_by_values(item: ObjectiveContribution) -> float:
    return max(abs(item.target), 1.0)


def _cosine_distance(observed: list[float], target: list[float]) -> float:
    observed_norm = math.sqrt(sum(value * value for value in observed))
    target_norm = math.sqrt(sum(value * value for value in target))
    if observed_norm == 0.0 or target_norm == 0.0:
        return 1.0 if observed != target else 0.0
    similarity = sum(a * b for a, b in zip(observed, target)) / (observed_norm * target_norm)
    return float(1.0 - max(-1.0, min(1.0, similarity)))


def _finite_float(value: Any) -> float | None:
    try:
        converted = float(value)
    except (TypeError, ValueError):
        return None
    return converted if math.isfinite(converted) else None


__all__ = [
    "ObjectiveContribution",
    "ObjectiveFunction",
    "ObjectiveResult",
    "SUPPORTED_OBJECTIVES",
    "compute_loss",
]
