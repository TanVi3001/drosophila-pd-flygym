"""Candidate phenotype model used before human approval."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping

from drosophila_pd.literature.models import PhenotypeRecord


CANDIDATE_FIELDS = (
    "candidate_id",
    "paper_id",
    "doi",
    "pmid",
    "citation",
    "journal",
    "year",
    "authors",
    "species",
    "gene",
    "genotype",
    "assay",
    "age_days",
    "sex",
    "walking_speed",
    "walking_speed_unit",
    "stride",
    "stride_unit",
    "pause",
    "turning",
    "climbing",
    "sample_size",
    "figure_reference",
    "table_reference",
    "supplementary_reference",
    "page",
    "notes",
    "confidence",
    "manual_review_required",
    "source_file",
)

_NUMERIC_FIELDS = frozenset(
    {
        "age_days",
        "year",
        "walking_speed",
        "stride",
        "pause",
        "turning",
        "climbing",
        "sample_size",
        "confidence",
    }
)


@dataclass(frozen=True)
class CandidatePhenotype:
    """A conservative, reviewable candidate; not an atlas record."""

    values: Mapping[str, Any]

    def __post_init__(self) -> None:
        unknown = sorted(set(self.values) - set(CANDIDATE_FIELDS))
        if unknown:
            raise ValueError(f"Unknown candidate fields: {unknown}")
        normalized = {field: self.values.get(field) for field in CANDIDATE_FIELDS}
        if not str(normalized["candidate_id"] or "").strip():
            raise ValueError("candidate_id must be non-empty.")
        for field in _NUMERIC_FIELDS:
            value = normalized[field]
            if value is not None and not _finite(value):
                raise ValueError(f"{field} must be finite when provided.")
        object.__setattr__(self, "values", normalized)

    @classmethod
    def from_mapping(
        cls,
        mapping: Mapping[str, Any],
        *,
        candidate_id: str | None = None,
        source_file: str | None = None,
    ) -> "CandidatePhenotype":
        aliases = {
            "id": "candidate_id",
            "walking_speed_mean": "walking_speed",
            "stride_length": "stride",
            "stride_length_mean": "stride",
            "pause_fraction": "pause",
            "turning_rate": "turning",
            "climbing_score": "climbing",
            "figure": "figure_reference",
            "table": "table_reference",
            "supplement": "supplementary_reference",
        }
        normalized: dict[str, Any] = {}
        for key, value in mapping.items():
            normalized[aliases.get(str(key), str(key))] = value
        if candidate_id is not None:
            normalized["candidate_id"] = candidate_id
        if source_file is not None:
            normalized["source_file"] = source_file
        normalized.setdefault("manual_review_required", True)
        return cls(_coerce_values(normalized))

    @property
    def candidate_id(self) -> str:
        return str(self.values["candidate_id"])

    def get(self, field: str, default: Any = None) -> Any:
        return self.values.get(field, default)

    def with_updates(self, updates: Mapping[str, Any]) -> "CandidatePhenotype":
        values = dict(self.values)
        values.update(updates)
        return CandidatePhenotype.from_mapping(values, source_file=self.get("source_file"))

    def to_mapping(self) -> dict[str, Any]:
        return dict(self.values)

    def to_phenotype_record(self) -> PhenotypeRecord:
        """Convert an approved candidate to the atlas model only on explicit call."""

        paper_id = self.get("paper_id") or self.candidate_id
        return PhenotypeRecord.from_mapping(
            {
                "paper_id": paper_id,
                "doi": self.get("doi"),
                "pmid": self.get("pmid"),
                "title": self.get("citation"),
                "journal": self.get("journal"),
                "year": self.get("year"),
                "authors": self.get("authors"),
                "species": self.get("species"),
                "strain": None,
                "genotype": self.get("genotype"),
                "gene": self.get("gene"),
                "mutation": None,
                "expression_system": None,
                "sex": self.get("sex"),
                "age_days": self.get("age_days"),
                "temperature": None,
                "assay": self.get("assay"),
                "arena": None,
                "lighting": None,
                "camera_fps": None,
                "walking_speed_mean": self.get("walking_speed"),
                "walking_speed_sd": None,
                "walking_speed_unit": self.get("walking_speed_unit"),
                "stride_length_mean": self.get("stride"),
                "pause_fraction": self.get("pause"),
                "turning_rate": self.get("turning"),
                "heading_variance": None,
                "climbing_score": self.get("climbing"),
                "step_frequency": None,
                "sample_size": self.get("sample_size"),
                "confidence_interval": None,
                "p_value": None,
                "effect_size": None,
                "figure_reference": self.get("figure_reference"),
                "table_reference": self.get("table_reference"),
                "supplementary_reference": self.get("supplementary_reference"),
                "notes": self.get("notes"),
                "quality_score": None,
                "evidence_level": "unclassified",
                "manual_review": True,
                "provenance": {
                    "paper": self.get("paper_id"),
                    "figure": self.get("figure_reference"),
                    "table": self.get("table_reference"),
                    "supplement": self.get("supplementary_reference"),
                    "page": self.get("page"),
                },
            }
        )


def _coerce_values(values: Mapping[str, Any]) -> dict[str, Any]:
    result = {field: values.get(field) for field in CANDIDATE_FIELDS}
    for field in _NUMERIC_FIELDS:
        value = result[field]
        if value in (None, ""):
            result[field] = None
            continue
        try:
            number = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{field} must be numeric: {value!r}") from error
        result[field] = int(number) if field == "sample_size" and number.is_integer() else number
    return result


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


__all__ = ["CANDIDATE_FIELDS", "CandidatePhenotype"]
