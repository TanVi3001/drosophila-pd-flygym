"""CSV literature-record contract for computational calibration.

Rows are intentionally empty in the repository template. Numeric values may
only be added from traceable sources by the research team.
"""

from __future__ import annotations

from dataclasses import dataclass
import csv
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

from drosophila_pd.parkinson.phenotype_database import PhenotypeTarget


LITERATURE_FIELDS = (
    "paper_id",
    "citation",
    "species",
    "genotype",
    "gene",
    "assay",
    "age_days",
    "temperature",
    "sex",
    "walking_speed",
    "walking_speed_unit",
    "stride_length",
    "stride_unit",
    "pause_fraction",
    "turning_rate",
    "heading_variance",
    "climbing_score",
    "sample_size",
    "mean",
    "std",
    "sem",
    "ci95",
    "notes",
    "quality_score",
    "evidence_level",
)

_NUMERIC_FIELDS = frozenset(
    {
        "age_days",
        "temperature",
        "walking_speed",
        "stride_length",
        "pause_fraction",
        "turning_rate",
        "heading_variance",
        "climbing_score",
        "sample_size",
        "mean",
        "std",
        "sem",
        "quality_score",
    }
)

_TARGET_FIELDS = (
    ("walking_speed", "walking_speed_unit"),
    ("stride_length", "stride_unit"),
    ("pause_fraction", None),
    ("turning_rate", None),
    ("heading_variance", None),
    ("climbing_score", None),
)


@dataclass(frozen=True)
class LiteratureRecord:
    """One row from the literature database, preserving source context."""

    values: dict[str, Any]

    def __post_init__(self) -> None:
        missing = [field for field in LITERATURE_FIELDS if field not in self.values]
        if missing:
            raise ValueError(f"Literature record is missing fields: {missing}")
        object.__setattr__(self, "values", dict(self.values))
        for field in ("paper_id", "citation", "species", "genotype", "assay", "evidence_level"):
            if not str(self.values[field] or "").strip():
                raise ValueError(f"{field} must be non-empty for populated records.")
        if self.values["walking_speed"] is not None and not str(self.values["walking_speed_unit"] or "").strip():
            raise ValueError("walking_speed_unit is required when walking_speed is provided.")
        if self.values["stride_length"] is not None and not str(self.values["stride_unit"] or "").strip():
            raise ValueError("stride_unit is required when stride_length is provided.")
        for field in _NUMERIC_FIELDS:
            value = self.values[field]
            if value is not None and not _finite(value):
                raise ValueError(f"{field} must be finite when provided.")

    def to_mapping(self) -> dict[str, Any]:
        return dict(self.values)

    @property
    def paper_id(self) -> str:
        return str(self.values["paper_id"])

    def to_targets(self) -> tuple[PhenotypeTarget, ...]:
        """Convert explicitly populated phenotype fields into target records."""

        targets: list[PhenotypeTarget] = []
        for metric, unit_field in _TARGET_FIELDS:
            value = self.values.get(metric)
            if value is None:
                continue
            unit = self.values.get(unit_field) if unit_field else None
            context = _model_context(self.values)
            targets.append(
                PhenotypeTarget(
                    target_id=f"{self.paper_id}:{metric}",
                    metric=metric,
                    source_id=self.paper_id,
                    citation=str(self.values["citation"]),
                    model_context=context,
                    assay=str(self.values["assay"]),
                    direction="target",
                    target_value=float(value),
                    unit=None if unit in (None, "") else str(unit),
                    notes=(None if self.values["notes"] in (None, "") else str(self.values["notes"])),
                )
            )
        return tuple(targets)


def load_literature_csv(path: str | Path) -> tuple[LiteratureRecord, ...]:
    """Load and validate a literature CSV without filling missing values."""

    source = Path(path)
    with source.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = tuple(reader.fieldnames or ())
        missing = [field for field in LITERATURE_FIELDS if field not in fields]
        if missing:
            raise ValueError(f"Literature CSV is missing required fields: {missing}")
        records = []
        for index, raw in enumerate(reader, start=2):
            values = {
                field: _parse_value(field, raw.get(field, ""))
                for field in LITERATURE_FIELDS
            }
            if not any(value not in (None, "") for value in values.values()):
                continue
            try:
                records.append(LiteratureRecord(values))
            except ValueError as error:
                raise ValueError(f"Invalid literature row {index}: {error}") from error
    return tuple(records)


def validate_literature_records(records: Iterable[LiteratureRecord]) -> dict[str, Any]:
    """Return a machine-readable contract summary."""

    record_list = tuple(records)
    paper_ids = [record.paper_id for record in record_list]
    duplicate_ids = sorted({item for item in paper_ids if paper_ids.count(item) > 1})
    target_count = sum(len(record.to_targets()) for record in record_list)
    errors = []
    if duplicate_ids:
        errors.append(f"duplicate paper_id values: {duplicate_ids}")
    return {
        "valid": not errors,
        "record_count": len(record_list),
        "target_count": target_count,
        "duplicate_paper_ids": duplicate_ids,
        "errors": errors,
        "numeric_values_are_explicit": True,
    }


def literature_records_to_targets(
    records: Iterable[LiteratureRecord],
) -> tuple[PhenotypeTarget, ...]:
    """Return only target values explicitly present in the supplied records."""

    targets: list[PhenotypeTarget] = []
    for record in records:
        targets.extend(record.to_targets())
    return tuple(targets)


def _parse_value(field: str, raw: Any) -> Any:
    if raw is None or str(raw).strip() == "":
        return None
    text = str(raw).strip()
    if field in _NUMERIC_FIELDS:
        try:
            value = float(text)
        except ValueError as error:
            raise ValueError(f"{field} must be numeric: {text!r}") from error
        if field == "sample_size" and value.is_integer():
            return int(value)
        return value
    return text


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _model_context(values: Mapping[str, Any]) -> str:
    parts = []
    for field in ("species", "genotype", "gene", "age_days", "temperature", "sex"):
        value = values.get(field)
        if value not in (None, ""):
            parts.append(f"{field}={value}")
    return "; ".join(parts) or "Literature context supplied by source record."


__all__ = [
    "LITERATURE_FIELDS",
    "LiteratureRecord",
    "literature_records_to_targets",
    "load_literature_csv",
    "validate_literature_records",
]
