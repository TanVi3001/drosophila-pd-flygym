"""Structural validation for signatures and normalized signature sets."""

from __future__ import annotations

import math
from collections import Counter
from typing import Any, Iterable, Mapping

from .signature import DiseaseSignature, SIGNATURE_FIELDS, UNAVAILABLE


def validate_signature(signature: DiseaseSignature | Mapping[str, Any]) -> dict[str, Any]:
    """Validate values without filling missing metrics."""

    issues: list[dict[str, Any]] = []
    values = signature.values() if isinstance(signature, DiseaseSignature) else _values(signature)
    unknown = sorted(set(values) - set(SIGNATURE_FIELDS))
    if unknown:
        issues.append({"code": "DIMENSION_MISMATCH", "fields": unknown, "message": "Unknown signature fields."})
    missing = []
    for field_name in SIGNATURE_FIELDS:
        if field_name not in values or values[field_name] in (None, "", UNAVAILABLE):
            missing.append(field_name)
            continue
        try:
            if not math.isfinite(float(values[field_name])):
                issues.append({"code": "NON_FINITE", "field": field_name, "message": "Metric must be finite."})
        except (TypeError, ValueError):
            issues.append({"code": "INVALID_VALUE", "field": field_name, "message": "Metric must be numeric or unavailable."})
    if missing:
        issues.append({"code": "MISSING_METRIC", "fields": missing, "message": "Metrics are unavailable and were not imputed."})
    blocking = [issue for issue in issues if issue["code"] in {"DIMENSION_MISMATCH", "NON_FINITE", "INVALID_VALUE"}]
    return {
        "signature_id": getattr(signature, "signature_id", None),
        "valid": not blocking,
        "status": "PASS" if not blocking and not missing else "PARTIAL" if not blocking else "FAILED",
        "issues": issues,
        "missing_metrics": missing,
    }


def validate_signatures(signatures: Iterable[DiseaseSignature]) -> dict[str, Any]:
    """Validate a collection for duplicates and consistent normalization."""

    values = tuple(signatures)
    reports = [validate_signature(signature) for signature in values]
    issues = [
        {"index": index, **issue}
        for index, report in enumerate(reports)
        for issue in report["issues"]
    ]
    identifiers = [signature.signature_id for signature in values if signature.signature_id]
    for identifier, count in Counter(identifiers).items():
        if count > 1:
            issues.append({"code": "DUPLICATE_SIGNATURE", "signature_id": identifier, "count": count, "message": "Signature identifiers must be unique."})
    consistency = validate_normalization_consistency(values)
    issues.extend(consistency["issues"])
    blocking = [issue for issue in issues if issue["code"] in {"DIMENSION_MISMATCH", "NON_FINITE", "INVALID_VALUE", "DUPLICATE_SIGNATURE", "NORMALIZATION_INCONSISTENCY"}]
    return {
        "valid": not blocking,
        "status": "PASS" if not blocking and not issues else "PARTIAL" if not blocking else "FAILED",
        "count": len(values),
        "issues": issues,
        "reports": reports,
    }


def validate_normalization_consistency(signatures: Iterable[DiseaseSignature]) -> dict[str, Any]:
    methods = {
        str(signature.metadata.get("normalization_method") or "raw")
        for signature in signatures
    }
    issues = []
    if len(methods) > 1:
        issues.append({"code": "NORMALIZATION_INCONSISTENCY", "methods": sorted(methods), "message": "Signatures use different normalization methods."})
    return {"valid": not issues, "issues": issues, "methods": sorted(methods)}


def _values(signature: Mapping[str, Any]) -> Mapping[str, Any]:
    nested = signature.get("values")
    if isinstance(nested, Mapping):
        return nested
    ignored = {"signature_id", "dataset_id", "source", "metadata", "schema_version", "scientific_scope"}
    return {key: value for key, value in signature.items() if key not in ignored}


__all__ = ["validate_normalization_consistency", "validate_signature", "validate_signatures"]
