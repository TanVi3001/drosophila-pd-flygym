"""Explicit, reference-driven normalization for computational signatures."""

from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import median
from typing import Any, Iterable, Mapping, Sequence

from .signature import DiseaseSignature, SIGNATURE_FIELDS, UNAVAILABLE


NORMALIZATION_METHODS = ("none", "zscore", "minmax", "robust", "healthy_baseline")


@dataclass(frozen=True)
class NormalizationResult:
    """A normalized signature and the statistics used to produce it."""

    signature: DiseaseSignature
    method: str
    statistics: Mapping[str, Any]


def normalize_signature(
    signature: DiseaseSignature,
    *,
    method: str,
    reference: Sequence[DiseaseSignature] | None = None,
    healthy_baseline: DiseaseSignature | None = None,
) -> NormalizationResult:
    """Normalize one signature using explicitly supplied reference data."""

    method = _method(method)
    if method == "none":
        return NormalizationResult(signature=signature, method=method, statistics={})
    if method == "healthy_baseline":
        if healthy_baseline is None:
            raise ValueError("healthy_baseline normalization requires a baseline signature.")
        normalized = {
            field_name: _difference(signature.value(field_name), healthy_baseline.value(field_name))
            for field_name in SIGNATURE_FIELDS
        }
        return NormalizationResult(
            signature=_replace(signature, normalized, method, {"baseline_id": healthy_baseline.signature_id}),
            method=method,
            statistics={"baseline_id": healthy_baseline.signature_id},
        )
    refs = tuple(reference or ())
    if not refs:
        raise ValueError(f"{method} normalization requires reference signatures.")
    statistics = _reference_statistics(refs, method)
    normalized = {
        field_name: _apply(signature.value(field_name), statistics[field_name], method)
        for field_name in SIGNATURE_FIELDS
    }
    return NormalizationResult(signature=_replace(signature, normalized, method, statistics), method=method, statistics=statistics)


def normalize_signatures(
    signatures: Iterable[DiseaseSignature],
    *,
    method: str,
    reference: Sequence[DiseaseSignature] | None = None,
    healthy_baseline: DiseaseSignature | None = None,
) -> tuple[NormalizationResult, ...]:
    """Normalize a collection while retaining per-field availability."""

    values = tuple(signatures)
    refs = tuple(reference) if reference is not None else values
    return tuple(
        normalize_signature(item, method=method, reference=refs, healthy_baseline=healthy_baseline)
        for item in values
    )


def _method(method: str) -> str:
    value = str(method).lower().replace("-", "_")
    aliases = {"min_max": "minmax", "healthy": "healthy_baseline", "baseline": "healthy_baseline"}
    value = aliases.get(value, value)
    if value not in NORMALIZATION_METHODS:
        raise ValueError(f"Unsupported normalization method: {method}")
    return value


def _reference_statistics(signatures: Sequence[DiseaseSignature], method: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for field_name in SIGNATURE_FIELDS:
        values = [float(signature.value(field_name)) for signature in signatures if _available(signature.value(field_name))]
        if not values:
            result[field_name] = {"status": UNAVAILABLE}
            continue
        if method == "zscore":
            center = sum(values) / len(values)
            spread = math.sqrt(sum((value - center) ** 2 for value in values) / len(values))
            result[field_name] = {"center": center, "spread": spread, "status": "available" if spread else UNAVAILABLE}
        elif method == "minmax":
            lower, upper = min(values), max(values)
            result[field_name] = {"min": lower, "max": upper, "status": "available" if upper != lower else UNAVAILABLE}
        else:
            center = median(values)
            spread = median([abs(value - center) for value in values])
            result[field_name] = {"center": center, "spread": spread, "status": "available" if spread else UNAVAILABLE}
    return result


def _apply(value: Any, stats: Mapping[str, Any], method: str) -> float | str:
    if value == UNAVAILABLE or stats.get("status") != "available":
        return UNAVAILABLE
    number = float(value)
    if method == "zscore":
        return (number - float(stats["center"])) / float(stats["spread"])
    if method == "minmax":
        return (number - float(stats["min"])) / (float(stats["max"]) - float(stats["min"]))
    return (number - float(stats["center"])) / float(stats["spread"])


def _difference(value: Any, baseline: Any) -> float | str:
    if value == UNAVAILABLE or baseline == UNAVAILABLE:
        return UNAVAILABLE
    return float(value) - float(baseline)


def _replace(signature: DiseaseSignature, values: Mapping[str, Any], method: str, statistics: Mapping[str, Any]) -> DiseaseSignature:
    return DiseaseSignature.from_mapping(
        values,
        signature_id=signature.signature_id,
        source=signature.source,
        metadata={**signature.metadata, "normalization_method": method, "normalization_statistics": statistics},
    )


def _available(value: Any) -> bool:
    try:
        return value != UNAVAILABLE and math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


__all__ = ["NORMALIZATION_METHODS", "NormalizationResult", "normalize_signature", "normalize_signatures"]
