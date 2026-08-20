"""Deterministic in-memory search helpers for atlas records."""

from __future__ import annotations

from typing import Iterable

from .models import METRIC_FIELDS, PhenotypeRecord


def find_by_gene(records: Iterable[PhenotypeRecord], gene: str) -> tuple[PhenotypeRecord, ...]:
    return _contains(records, "gene", gene)


def find_by_assay(records: Iterable[PhenotypeRecord], assay: str) -> tuple[PhenotypeRecord, ...]:
    return _contains(records, "assay", assay)


def find_by_genotype(records: Iterable[PhenotypeRecord], genotype: str) -> tuple[PhenotypeRecord, ...]:
    return _contains(records, "genotype", genotype)


def find_by_metric(records: Iterable[PhenotypeRecord], metric: str) -> tuple[PhenotypeRecord, ...]:
    if metric not in METRIC_FIELDS:
        raise ValueError(f"Unsupported atlas metric: {metric}")
    return tuple(record for record in records if record.metric_value(metric) is not None)


def find_by_year(records: Iterable[PhenotypeRecord], year: int) -> tuple[PhenotypeRecord, ...]:
    return tuple(record for record in records if _number_equals(record.get("year"), year))


def find_by_quality(records: Iterable[PhenotypeRecord], minimum: float) -> tuple[PhenotypeRecord, ...]:
    if minimum < 0 or minimum > 1:
        raise ValueError("minimum quality must be in [0, 1].")
    return tuple(
        record
        for record in records
        if _number(record.get("quality_score")) is not None
        and _number(record.get("quality_score")) >= minimum
    )


def _contains(records: Iterable[PhenotypeRecord], field: str, value: str) -> tuple[PhenotypeRecord, ...]:
    needle = value.strip().lower()
    if not needle:
        return ()
    return tuple(
        record
        for record in records
        if needle in str(record.get(field) or "").lower()
    )


def _number(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _number_equals(value: object, expected: int) -> bool:
    number = _number(value)
    return number is not None and number == expected


__all__ = [
    "find_by_assay",
    "find_by_gene",
    "find_by_genotype",
    "find_by_metric",
    "find_by_quality",
    "find_by_year",
]
