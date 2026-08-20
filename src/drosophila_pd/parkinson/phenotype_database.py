"""Validated literature-observation records for computational calibration.

This module stores provenance and target definitions.  It does not claim that
an observation is biological ground truth, and it never supplies missing
numeric values automatically.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any, Iterable


ALLOWED_DIRECTIONS = frozenset({"lower", "higher", "target"})


@dataclass(frozen=True)
class PhenotypeTarget:
    """One provenance-bearing literature observation or target."""

    target_id: str
    metric: str
    source_id: str
    citation: str
    model_context: str
    assay: str
    direction: str
    target_value: float | None = None
    target_range: tuple[float, float] | None = None
    unit: str | None = None
    weight: float = 1.0
    scale: float | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "target_id",
            "metric",
            "source_id",
            "citation",
            "model_context",
            "assay",
        ):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"{field_name} must be a non-empty string.")
        direction = str(self.direction).strip().lower()
        if direction not in ALLOWED_DIRECTIONS:
            raise ValueError(f"direction must be one of {sorted(ALLOWED_DIRECTIONS)}.")
        if self.target_value is not None and not _finite(self.target_value):
            raise ValueError("target_value must be finite.")
        if self.target_range is not None:
            if len(self.target_range) != 2 or not all(_finite(value) for value in self.target_range):
                raise ValueError("target_range must contain two finite values.")
            if float(self.target_range[0]) > float(self.target_range[1]):
                raise ValueError("target_range lower bound must not exceed upper bound.")
        if float(self.weight) <= 0 or not _finite(self.weight):
            raise ValueError("weight must be finite and positive.")
        if self.scale is not None and (float(self.scale) <= 0 or not _finite(self.scale)):
            raise ValueError("scale must be finite and positive when provided.")
        object.__setattr__(self, "direction", direction)
        object.__setattr__(self, "target_value", None if self.target_value is None else float(self.target_value))
        object.__setattr__(
            self,
            "target_range",
            None if self.target_range is None else tuple(float(value) for value in self.target_range),
        )
        object.__setattr__(self, "weight", float(self.weight))
        object.__setattr__(self, "scale", None if self.scale is None else float(self.scale))

    @property
    def numeric(self) -> bool:
        """Whether this target can participate in numeric calibration."""

        return self.target_value is not None or self.target_range is not None

    def to_mapping(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""

        result: dict[str, Any] = {
            "target_id": self.target_id,
            "metric": self.metric,
            "source_id": self.source_id,
            "citation": self.citation,
            "model_context": self.model_context,
            "assay": self.assay,
            "direction": self.direction,
            "weight": self.weight,
        }
        if self.target_value is not None:
            result["target_value"] = self.target_value
        if self.target_range is not None:
            result["target_range"] = list(self.target_range)
        if self.unit is not None:
            result["unit"] = self.unit
        if self.scale is not None:
            result["scale"] = self.scale
        if self.notes is not None:
            result["notes"] = self.notes
        return result


@dataclass(frozen=True)
class PhenotypeDatabase:
    """A validated set of literature observations and calibration targets."""

    schema_version: str
    targets: tuple[PhenotypeTarget, ...]
    metadata: dict[str, Any]
    source_path: str | None = None

    @property
    def numeric_targets(self) -> tuple[PhenotypeTarget, ...]:
        return tuple(target for target in self.targets if target.numeric)

    @property
    def qualitative_targets(self) -> tuple[PhenotypeTarget, ...]:
        return tuple(target for target in self.targets if not target.numeric)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "metadata": dict(self.metadata),
            "targets": [target.to_mapping() for target in self.targets],
        }


def load_phenotype_database(path: str | Path) -> PhenotypeDatabase:
    """Load and validate a phenotype database JSON document."""

    source = Path(path)
    with source.open("r", encoding="utf-8") as handle:
        document = json.load(handle)
    database = phenotype_database_from_mapping(document, source_path=str(source))
    return database


def phenotype_database_from_mapping(
    document: dict[str, Any], *, source_path: str | None = None
) -> PhenotypeDatabase:
    """Build a validated database from a JSON-compatible mapping."""

    if not isinstance(document, dict):
        raise ValueError("Phenotype database root must be a mapping.")
    schema_version = document.get("schema_version")
    if not isinstance(schema_version, str) or not schema_version.strip():
        raise ValueError("schema_version must be a non-empty string.")
    raw_targets = document.get("targets")
    if not isinstance(raw_targets, list):
        raise ValueError("targets must be a list.")
    targets = tuple(_target_from_mapping(item, index=index) for index, item in enumerate(raw_targets))
    ids = [target.target_id for target in targets]
    if len(ids) != len(set(ids)):
        raise ValueError("target_id values must be unique.")
    metadata = document.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a mapping.")
    return PhenotypeDatabase(
        schema_version=schema_version,
        targets=targets,
        metadata=dict(metadata),
        source_path=source_path,
    )


def validate_phenotype_document(document: dict[str, Any]) -> dict[str, Any]:
    """Return a machine-readable validation summary without loading a file."""

    try:
        database = phenotype_database_from_mapping(document)
    except (TypeError, ValueError) as error:
        return {"valid": False, "error": str(error)}
    return {
        "valid": True,
        "target_count": len(database.targets),
        "numeric_target_count": len(database.numeric_targets),
        "qualitative_target_count": len(database.qualitative_targets),
    }


def _target_from_mapping(item: Any, *, index: int) -> PhenotypeTarget:
    if not isinstance(item, dict):
        raise ValueError(f"targets[{index}] must be a mapping.")
    target_range = item.get("target_range")
    if target_range is not None:
        if not isinstance(target_range, (list, tuple)):
            raise ValueError(f"targets[{index}].target_range must be a list.")
        target_range = tuple(float(value) for value in target_range)
    return PhenotypeTarget(
        target_id=str(item.get("target_id", "")),
        metric=str(item.get("metric", "")),
        source_id=str(item.get("source_id", "")),
        citation=str(item.get("citation", "")),
        model_context=str(item.get("model_context", "")),
        assay=str(item.get("assay", "")),
        direction=str(item.get("direction", "")),
        target_value=item.get("target_value"),
        target_range=target_range,
        unit=None if item.get("unit") is None else str(item["unit"]),
        weight=item.get("weight", 1.0),
        scale=item.get("scale"),
        notes=None if item.get("notes") is None else str(item["notes"]),
    )


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


__all__ = [
    "ALLOWED_DIRECTIONS",
    "PhenotypeDatabase",
    "PhenotypeTarget",
    "load_phenotype_database",
    "phenotype_database_from_mapping",
    "validate_phenotype_document",
]
