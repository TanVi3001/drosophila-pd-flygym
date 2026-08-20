"""Validation rules for literature candidates, without scientific inference."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Iterable

from .candidate import CandidatePhenotype


def validate_candidate(candidate: CandidatePhenotype) -> dict[str, Any]:
    """Return actionable validation issues for one candidate."""

    issues: list[dict[str, str]] = []

    def missing(code: str, field: str) -> None:
        if not str(candidate.get(field) or "").strip():
            issues.append({"code": code, "field": field, "message": f"Missing {field}."})

    missing("MISSING_PROVENANCE", "paper_id")
    missing("MISSING_PROVENANCE", "citation")
    missing("MISSING_PROVENANCE", "page")
    missing("MISSING_PROVENANCE", "table_reference")
    missing("MISSING_PROVENANCE", "supplementary_reference")
    missing("MISSING_FIGURE", "figure_reference")
    missing("MISSING_ASSAY", "assay")
    if candidate.get("walking_speed") is not None:
        missing("MISSING_UNIT", "walking_speed_unit")
    if candidate.get("stride") is not None:
        missing("MISSING_UNIT", "stride_unit")

    confidence = candidate.get("confidence")
    if confidence is not None and (not _finite(confidence) or not 0 <= float(confidence) <= 1):
        issues.append({"code": "INVALID_CONFIDENCE", "field": "confidence", "message": "confidence must be in [0, 1]."})

    return {
        "candidate_id": candidate.candidate_id,
        "valid": not issues,
        "issues": issues,
        "blocking": [issue for issue in issues if issue["code"] in _BLOCKING_CODES],
    }


def validate_candidates(candidates: Iterable[CandidatePhenotype]) -> dict[str, Any]:
    """Validate candidates and detect duplicate DOI values."""

    materialized = tuple(candidates)
    reports = {candidate.candidate_id: validate_candidate(candidate) for candidate in materialized}
    by_doi: defaultdict[str, list[str]] = defaultdict(list)
    for candidate in materialized:
        doi = str(candidate.get("doi") or "").strip().lower()
        if doi:
            by_doi[doi].append(candidate.candidate_id)
    for doi, candidate_ids in by_doi.items():
        if len(candidate_ids) < 2:
            continue
        for candidate_id in candidate_ids:
            issue = {"code": "DUPLICATE_DOI", "field": "doi", "message": f"DOI {doi!r} occurs in {candidate_ids}."}
            reports[candidate_id]["issues"].append(issue)
            reports[candidate_id]["blocking"].append(issue)
            reports[candidate_id]["valid"] = False

    return {
        "valid": all(report["valid"] for report in reports.values()),
        "candidate_count": len(materialized),
        "reports": reports,
        "issues": [
            {"candidate_id": candidate_id, **issue}
            for candidate_id, report in reports.items()
            for issue in report["issues"]
        ],
    }


_BLOCKING_CODES = frozenset(
    {"DUPLICATE_DOI", "MISSING_PROVENANCE", "MISSING_FIGURE", "MISSING_ASSAY", "MISSING_UNIT", "INVALID_CONFIDENCE"}
)


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


__all__ = ["validate_candidate", "validate_candidates"]
