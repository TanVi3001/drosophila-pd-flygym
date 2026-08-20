"""Structural and provenance validation for atlas records."""

from __future__ import annotations

import math
from typing import Any, Iterable

from .models import EVIDENCE_LEVELS, PhenotypeRecord


def validate_database(records: Iterable[PhenotypeRecord]) -> dict[str, Any]:
    """Return validation findings without modifying or scoring records."""

    record_list = tuple(records)
    issues: list[dict[str, Any]] = []
    doi_counts = _counts(record.get("doi") for record in record_list)
    pmid_counts = _counts(record.get("pmid") for record in record_list)
    for identifier_type, counts in (("doi", doi_counts), ("pmid", pmid_counts)):
        for identifier, count in counts.items():
            if count > 1:
                issues.append(
                    {
                        "type": f"DUPLICATE_{identifier_type.upper()}",
                        "value": identifier,
                        "count": count,
                    }
                )
    for index, record in enumerate(record_list):
        for issue in _record_issues(record):
            issues.append({"record_index": index, "paper_id": record.paper_id, **issue})
    errors = [item for item in issues if item["type"] not in {"MISSING_OPTIONAL_CONTEXT"}]
    return {
        "valid": not errors,
        "record_count": len(record_list),
        "error_count": len(errors),
        "issue_count": len(issues),
        "issues": issues,
        "duplicate_doi_count": sum(count > 1 for count in doi_counts.values()),
        "duplicate_pmid_count": sum(count > 1 for count in pmid_counts.values()),
        "scientific_scope": "Structural literature curation only; no automatic evidence judgment.",
    }


def _record_issues(record: PhenotypeRecord) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if not str(record.get("assay") or "").strip():
        issues.append({"type": "MISSING_ASSAY"})
    citation_fields = ("title", "journal", "authors", "year")
    if any(record.get(field) in (None, "") for field in citation_fields):
        issues.append({"type": "MISSING_CITATION"})
    if record.get("sample_size") in (None, ""):
        issues.append({"type": "MISSING_SAMPLE_SIZE"})
    provenance_missing = record.provenance_record.missing_fields()
    if provenance_missing:
        issues.append(
            {
                "type": "MISSING_PROVENANCE",
                "fields": ",".join(provenance_missing),
            }
        )
    if record.metric_value("walking_speed_mean") is not None and not str(record.get("walking_speed_unit") or "").strip():
        issues.append({"type": "MISSING_UNIT", "metric": "walking_speed_mean"})
    if record.metric_value("stride_length_mean") is not None and not str(record.get("walking_speed_unit") or "").strip():
        issues.append({"type": "MISSING_UNIT", "metric": "stride_length_mean"})
    quality = record.get("quality_score")
    if quality not in (None, ""):
        try:
            valid_quality = math.isfinite(float(quality)) and 0.0 <= float(quality) <= 1.0
        except (TypeError, ValueError):
            valid_quality = False
        if not valid_quality:
            issues.append({"type": "INVALID_QUALITY_SCORE"})
    evidence = str(record.get("evidence_level") or "").strip()
    if evidence and evidence not in EVIDENCE_LEVELS:
        issues.append({"type": "INVALID_EVIDENCE_LEVEL", "value": evidence})
    return issues


def _counts(values: Iterable[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        text = str(value or "").strip()
        if text:
            counts[text] = counts.get(text, 0) + 1
    return counts


__all__ = ["validate_database"]
