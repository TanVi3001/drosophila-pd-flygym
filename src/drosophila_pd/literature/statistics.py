"""Descriptive coverage summaries for the atlas, without automatic scoring."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .models import METRIC_FIELDS, PhenotypeRecord


def build_statistics(records: Iterable[PhenotypeRecord]) -> dict[str, Any]:
    record_list = tuple(records)
    field_coverage = {
        field: sum(record.get(field) not in (None, "") for record in record_list)
        for field in record_list[0].values
    } if record_list else {}
    return {
        "coverage": {
            "record_count": len(record_list),
            "field_coverage": field_coverage,
            "metric_coverage": {
                metric: sum(record.metric_value(metric) is not None for record in record_list)
                for metric in METRIC_FIELDS
            },
        },
        "gene_summary": _group_summary(record_list, "gene"),
        "assay_summary": _group_summary(record_list, "assay"),
        "phenotype_summary": _phenotype_summary(record_list),
        "quality_distribution": _quality_distribution(record_list),
        "scientific_scope": "Descriptive curation coverage; no evidence score is inferred.",
    }


def _group_summary(records: tuple[PhenotypeRecord, ...], field: str) -> list[dict[str, Any]]:
    groups: dict[str, list[PhenotypeRecord]] = {}
    for record in records:
        value = str(record.get(field) or "").strip()
        if value:
            groups.setdefault(value, []).append(record)
    return [
        {
            "value": value,
            "record_count": len(items),
            "metric_count": sum(len(item.populated_metrics()) for item in items),
        }
        for value, items in sorted(groups.items())
    ]


def _phenotype_summary(records: tuple[PhenotypeRecord, ...]) -> list[dict[str, Any]]:
    return [
        {
            "metric": metric,
            "record_count": len(records),
            "available_count": sum(record.metric_value(metric) is not None for record in records),
            "missing_count": sum(record.metric_value(metric) is None for record in records),
        }
        for metric in METRIC_FIELDS
    ]


def _quality_distribution(records: tuple[PhenotypeRecord, ...]) -> list[dict[str, Any]]:
    buckets = Counter()
    for record in records:
        value = record.get("quality_score")
        if value in (None, ""):
            buckets["unscored"] += 1
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            buckets["invalid"] += 1
        else:
            if number < 0.25:
                buckets["0.00-0.24"] += 1
            elif number < 0.50:
                buckets["0.25-0.49"] += 1
            elif number < 0.75:
                buckets["0.50-0.74"] += 1
            else:
                buckets["0.75-1.00"] += 1
    return [
        {"bucket": bucket, "record_count": buckets[bucket]}
        for bucket in sorted(buckets)
    ]


__all__ = ["build_statistics"]
