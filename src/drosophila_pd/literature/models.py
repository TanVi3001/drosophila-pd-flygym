"""Data models and field contracts for the Digital Phenotype Atlas."""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from typing import Any, Mapping


PHENOTYPE_ATLAS_FIELDS = (
    "paper_id",
    "doi",
    "pmid",
    "title",
    "journal",
    "year",
    "authors",
    "species",
    "strain",
    "genotype",
    "gene",
    "mutation",
    "expression_system",
    "sex",
    "age_days",
    "temperature",
    "assay",
    "arena",
    "lighting",
    "camera_fps",
    "walking_speed_mean",
    "walking_speed_sd",
    "walking_speed_unit",
    "stride_length_mean",
    "pause_fraction",
    "turning_rate",
    "heading_variance",
    "climbing_score",
    "step_frequency",
    "sample_size",
    "confidence_interval",
    "p_value",
    "effect_size",
    "figure_reference",
    "table_reference",
    "supplementary_reference",
    "notes",
    "quality_score",
    "evidence_level",
    "manual_review",
    "provenance",
)

METRIC_FIELDS = (
    "walking_speed_mean",
    "stride_length_mean",
    "pause_fraction",
    "turning_rate",
    "heading_variance",
    "climbing_score",
    "step_frequency",
)

EVIDENCE_LEVELS = frozenset(
    {
        "peer_reviewed_primary",
        "peer_reviewed_secondary",
        "preprint",
        "unclassified",
    }
)

_NUMERIC_FIELDS = frozenset(
    {
        "year",
        "age_days",
        "temperature",
        "camera_fps",
        *METRIC_FIELDS,
        "walking_speed_sd",
        "sample_size",
        "quality_score",
    }
)


@dataclass(frozen=True)
class Provenance:
    """Traceability pointers supplied by a curator, never inferred."""

    paper: str | None = None
    figure: str | None = None
    table: str | None = None
    supplement: str | None = None
    page: str | None = None

    @classmethod
    def from_value(cls, value: Any) -> "Provenance":
        if isinstance(value, Provenance):
            return value
        if isinstance(value, Mapping):
            return cls(**{key: _text(value.get(key)) for key in cls.__dataclass_fields__})
        if value in (None, ""):
            return cls()
        text = str(value).strip()
        try:
            decoded = json.loads(text)
        except json.JSONDecodeError:
            decoded = {
                part.split("=", 1)[0].strip(): part.split("=", 1)[1].strip()
                for part in text.split(";")
                if "=" in part
            }
        if not isinstance(decoded, Mapping):
            raise ValueError("provenance must be a mapping or key=value list.")
        return cls.from_value(decoded)

    def missing_fields(self) -> tuple[str, ...]:
        return tuple(
            field
            for field in self.__dataclass_fields__
            if not str(getattr(self, field) or "").strip()
        )

    def to_mapping(self) -> dict[str, str | None]:
        return {field: getattr(self, field) for field in self.__dataclass_fields__}

    def to_json(self) -> str:
        return json.dumps(self.to_mapping(), sort_keys=True)


@dataclass(frozen=True)
class PhenotypeRecord:
    """One curated row, retaining blank fields as unavailable values."""

    values: Mapping[str, Any]

    def __post_init__(self) -> None:
        unknown = sorted(set(self.values) - set(PHENOTYPE_ATLAS_FIELDS))
        if unknown:
            raise ValueError(f"Unknown phenotype fields: {unknown}")
        normalized = {field: self.values.get(field) for field in PHENOTYPE_ATLAS_FIELDS}
        object.__setattr__(self, "values", normalized)

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> "PhenotypeRecord":
        return cls(values)

    def get(self, field: str, default: Any = None) -> Any:
        return self.values.get(field, default)

    def metric_value(self, metric: str) -> float | None:
        if metric not in METRIC_FIELDS:
            raise ValueError(f"Unsupported atlas metric: {metric}")
        value = self.get(metric)
        try:
            converted = float(value)
        except (TypeError, ValueError):
            return None
        return converted if math.isfinite(converted) else None

    @property
    def paper_id(self) -> str:
        return str(self.get("paper_id") or "")

    @property
    def provenance_record(self) -> Provenance:
        return Provenance.from_value(self.get("provenance"))

    def populated_metrics(self) -> tuple[str, ...]:
        return tuple(metric for metric in METRIC_FIELDS if self.metric_value(metric) is not None)

    def to_mapping(self) -> dict[str, Any]:
        result = dict(self.values)
        provenance = result.get("provenance")
        if isinstance(provenance, Provenance):
            result["provenance"] = provenance.to_mapping()
        return result


def _text(value: Any) -> str | None:
    return None if value in (None, "") else str(value)


__all__ = [
    "EVIDENCE_LEVELS",
    "METRIC_FIELDS",
    "PHENOTYPE_ATLAS_FIELDS",
    "PhenotypeRecord",
    "Provenance",
]
