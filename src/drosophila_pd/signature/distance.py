"""Distance interfaces for computational signature comparison."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping

import numpy as np

from .embedding import SignatureEmbedding
from .signature import DiseaseSignature, SIGNATURE_FIELDS, UNAVAILABLE


@dataclass(frozen=True)
class DistanceResult:
    """A distance result with the fields and availability used."""

    metric: str
    distance: float | None
    status: str
    fields: tuple[str, ...] = ()
    reason: str | None = None

    @property
    def available(self) -> bool:
        return self.status == "PASS" and self.distance is not None

    def to_mapping(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "distance": self.distance,
            "status": self.status,
            "fields": list(self.fields),
            "reason": self.reason,
        }


def euclidean_distance(first: Any, second: Any) -> DistanceResult:
    fields, values_first, values_second = _shared_values(first, second)
    if not fields:
        return _unavailable("euclidean", "No shared available metrics.")
    return DistanceResult("euclidean", float(np.linalg.norm(values_first - values_second)), "PASS", fields)


def weighted_euclidean_distance(first: Any, second: Any, *, weights: Mapping[str, float]) -> DistanceResult:
    fields, values_first, values_second = _shared_values(first, second)
    if not fields:
        return _unavailable("weighted_euclidean", "No shared available metrics.")
    missing_weights = [field_name for field_name in fields if field_name not in weights]
    if missing_weights:
        return _unavailable("weighted_euclidean", f"Missing weights for: {missing_weights}")
    weight_values = np.asarray([float(weights[field_name]) for field_name in fields], dtype=float)
    if not np.isfinite(weight_values).all() or (weight_values < 0).any() or not np.any(weight_values > 0):
        return _unavailable("weighted_euclidean", "Weights must be finite, non-negative, and not all zero.")
    distance = math.sqrt(float(np.sum(weight_values * (values_first - values_second) ** 2)))
    return DistanceResult("weighted_euclidean", distance, "PASS", fields)


def cosine_distance(first: Any, second: Any) -> DistanceResult:
    fields, values_first, values_second = _shared_values(first, second)
    if not fields:
        return _unavailable("cosine", "No shared available metrics.")
    norm_first = float(np.linalg.norm(values_first))
    norm_second = float(np.linalg.norm(values_second))
    if norm_first == 0 or norm_second == 0:
        return _unavailable("cosine", "Cosine distance is undefined for a zero vector.")
    similarity = float(np.dot(values_first, values_second) / (norm_first * norm_second))
    return DistanceResult("cosine", 1.0 - similarity, "PASS", fields)


def mahalanobis_distance(first: Any, second: Any, *, covariance: Any | None = None) -> DistanceResult:
    """Interface for Mahalanobis distance; covariance is intentionally explicit."""

    if covariance is None:
        return _unavailable("mahalanobis", "Interface only until a validated covariance is supplied.")
    fields, values_first, values_second = _shared_values(first, second)
    if not fields:
        return _unavailable("mahalanobis", "No shared available metrics.")
    matrix = np.asarray(covariance, dtype=float)
    if matrix.shape != (len(fields), len(fields)) or not np.isfinite(matrix).all():
        return _unavailable("mahalanobis", "Covariance shape or values are invalid.")
    delta = values_first - values_second
    distance = math.sqrt(max(0.0, float(delta @ np.linalg.pinv(matrix) @ delta)))
    return DistanceResult("mahalanobis", distance, "PASS", fields)


def dynamic_time_warping_distance(first: Any, second: Any) -> DistanceResult:
    """Reserved interface; time-series signatures are not implemented here."""

    return _unavailable("dtw", "Interface only; DiseaseSignature contains summary metrics, not time series.")


def earth_mover_distance(first: Any, second: Any) -> DistanceResult:
    """Reserved interface; no external distribution package is required."""

    return _unavailable("earth_mover", "Interface only; distribution inputs are not part of DiseaseSignature.")


def _shared_values(first: Any, second: Any) -> tuple[tuple[str, ...], np.ndarray, np.ndarray]:
    first_values = _as_mapping(first)
    second_values = _as_mapping(second)
    fields = tuple(
        field_name
        for field_name in SIGNATURE_FIELDS
        if _available(first_values.get(field_name)) and _available(second_values.get(field_name))
    )
    return (
        fields,
        np.asarray([float(first_values[field_name]) for field_name in fields], dtype=float),
        np.asarray([float(second_values[field_name]) for field_name in fields], dtype=float),
    )


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, DiseaseSignature):
        return value.values()
    if isinstance(value, SignatureEmbedding):
        return value.field_values()
    if isinstance(value, Mapping):
        nested = value.get("values")
        return nested if isinstance(nested, Mapping) else value
    raise TypeError("Distance inputs must be DiseaseSignature, SignatureEmbedding, or a mapping.")


def _available(value: Any) -> bool:
    try:
        return value != UNAVAILABLE and math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _unavailable(metric: str, reason: str) -> DistanceResult:
    return DistanceResult(metric, None, "UNAVAILABLE", reason=reason)


__all__ = [
    "DistanceResult",
    "cosine_distance",
    "dynamic_time_warping_distance",
    "earth_mover_distance",
    "euclidean_distance",
    "mahalanobis_distance",
    "weighted_euclidean_distance",
]
