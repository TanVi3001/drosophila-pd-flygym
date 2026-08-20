"""Provenance helpers for paper-to-evidence traceability."""

from __future__ import annotations

from typing import Any, Mapping

from .models import PhenotypeRecord, Provenance


def parse_provenance(value: Any) -> Provenance:
    """Parse curator-supplied provenance without filling missing pointers."""

    return Provenance.from_value(value)


def validate_provenance(value: Any) -> dict[str, Any]:
    provenance = parse_provenance(value)
    missing = provenance.missing_fields()
    return {
        "valid": not missing,
        "missing_fields": list(missing),
        "provenance": provenance.to_mapping(),
    }


def record_provenance(record: PhenotypeRecord) -> dict[str, Any]:
    """Return a non-mutating provenance summary for one atlas record."""

    result = validate_provenance(record.get("provenance"))
    result["paper_id"] = record.paper_id
    return result


__all__ = ["parse_provenance", "record_provenance", "validate_provenance"]
