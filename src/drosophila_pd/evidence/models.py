"""Data models for literature evidence assessment.

The models in this module represent evidence completeness and provenance.
They do not represent biological disease state or simulation parameters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from pathlib import Path
from typing import Any, Mapping


EXPECTED_PROXIES = (
    "motor_vigor",
    "coordination",
    "delay",
    "noise",
    "fatigue",
    "latency",
    "asymmetry",
    "freezing",
    "postural_instability",
)

CONFIDENCE_WEIGHTS = {
    "HIGH": 1.0,
    "MEDIUM": 0.6,
    "LOW": 0.3,
    "NONE": 0.0,
}


@dataclass(frozen=True)
class EvidenceCriterion:
    """One configurable evidence criterion."""

    name: str
    weight: float
    description: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("evidence criterion name must not be empty")
        if not math.isfinite(float(self.weight)) or float(self.weight) < 0:
            raise ValueError(f"invalid weight for evidence criterion: {self.name}")


@dataclass(frozen=True)
class ScoringConfig:
    """Configurable scoring policy for evidence completeness."""

    criteria: tuple[EvidenceCriterion, ...]
    expected_proxies: tuple[str, ...] = EXPECTED_PROXIES
    high_threshold: float = 75.0
    medium_threshold: float = 50.0

    def __post_init__(self) -> None:
        names = [criterion.name for criterion in self.criteria]
        if len(names) != len(set(names)):
            raise ValueError("evidence criterion names must be unique")
        if not self.criteria:
            raise ValueError("at least one evidence criterion is required")
        if self.high_threshold < self.medium_threshold:
            raise ValueError("high threshold must be >= medium threshold")
        if self.medium_threshold < 0:
            raise ValueError("medium threshold must be non-negative")

    @property
    def total_weight(self) -> float:
        return sum(float(criterion.weight) for criterion in self.criteria)

    def level_for(self, score: float) -> str:
        if score >= self.high_threshold:
            return "HIGH"
        if score >= self.medium_threshold:
            return "MEDIUM"
        return "LOW"

    def as_dict(self) -> dict[str, Any]:
        return {
            "criteria": [
                {
                    "name": criterion.name,
                    "weight": criterion.weight,
                    "description": criterion.description,
                }
                for criterion in self.criteria
            ],
            "expected_proxies": list(self.expected_proxies),
            "high_threshold": self.high_threshold,
            "medium_threshold": self.medium_threshold,
            "total_weight": self.total_weight,
        }


@dataclass(frozen=True)
class MappingEvidence:
    """One phenotype-to-proxy mapping row from the curation workspace."""

    paper_id: str
    phenotype: str
    metric: str
    disease_layer_proxy: str
    confidence: str
    reason: str
    recommended_use: str
    calibration_candidate: str
    validation_candidate: str
    manual_review_required: bool
    notes: str

    @classmethod
    def from_row(cls, row: Mapping[str, str]) -> "MappingEvidence":
        required = ("paper_id", "phenotype", "disease_layer_proxy", "confidence")
        missing = [name for name in required if not str(row.get(name, "")).strip()]
        if missing:
            raise ValueError(f"mapping row is missing required values: {', '.join(missing)}")
        confidence = str(row.get("confidence", "")).strip().upper()
        if confidence not in CONFIDENCE_WEIGHTS:
            raise ValueError(f"unsupported mapping confidence: {confidence}")
        return cls(
            paper_id=str(row["paper_id"]).strip(),
            phenotype=str(row.get("phenotype", "")).strip(),
            metric=str(row.get("metric", "")).strip(),
            disease_layer_proxy=str(row.get("disease_layer_proxy", "")).strip(),
            confidence=confidence,
            reason=str(row.get("reason", "")).strip(),
            recommended_use=str(row.get("recommended_use", "")).strip(),
            calibration_candidate=str(row.get("calibration_candidate", "")).strip().lower(),
            validation_candidate=str(row.get("validation_candidate", "")).strip().lower(),
            manual_review_required=_as_bool(row.get("manual_review_required", "")),
            notes=str(row.get("notes", "")).strip(),
        )

    @property
    def confidence_weight(self) -> float:
        return CONFIDENCE_WEIGHTS[self.confidence]

    def as_dict(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "phenotype": self.phenotype,
            "metric": self.metric,
            "disease_layer_proxy": self.disease_layer_proxy,
            "confidence": self.confidence,
            "confidence_weight": self.confidence_weight,
            "reason": self.reason,
            "recommended_use": self.recommended_use,
            "calibration_candidate": self.calibration_candidate,
            "validation_candidate": self.validation_candidate,
            "manual_review_required": self.manual_review_required,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class PaperEvidence:
    """Joined paper metadata, candidate review and mapping evidence."""

    paper_id: str
    paper: Mapping[str, Any]
    candidate: Mapping[str, str]
    mappings: tuple[MappingEvidence, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "paper": dict(self.paper),
            "candidate": dict(self.candidate),
            "mappings": [mapping.as_dict() for mapping in self.mappings],
        }


@dataclass(frozen=True)
class EvidenceScore:
    """Evidence completeness score for one paper."""

    paper_id: str
    score: float
    level: str
    criteria: Mapping[str, float]
    weighted_criteria: Mapping[str, float]
    quantitative_metric: bool
    protocol_available: bool
    sample_size_available: bool
    calibration_candidate: bool
    validation_candidate: bool
    proxy_names: tuple[str, ...]
    mapping_count: int
    manual_review_required: bool
    notes: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "evidence_score": self.score,
            "evidence_level": self.level,
            "criteria": dict(self.criteria),
            "weighted_criteria": dict(self.weighted_criteria),
            "quantitative_metric": self.quantitative_metric,
            "protocol_available": self.protocol_available,
            "sample_size_available": self.sample_size_available,
            "calibration_candidate": self.calibration_candidate,
            "validation_candidate": self.validation_candidate,
            "proxy_names": list(self.proxy_names),
            "mapping_count": self.mapping_count,
            "manual_review_required": self.manual_review_required,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class CoverageRow:
    """Coverage summary for one Disease Layer proxy."""

    proxy: str
    paper_count: int
    mapping_record_count: int
    quantitative_paper_count: int
    qualitative_paper_count: int
    calibration_candidate_count: int
    validation_candidate_count: int
    coverage_status: str

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class ImportanceRow:
    """Evidence-presence ranking for one proxy."""

    rank: int
    proxy: str
    paper_count: int
    total_evidence_score: float
    mean_evidence_score: float
    quantitative_paper_count: int
    coverage_status: str

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class DependencyRow:
    """Aggregated metric-to-proxy dependency row."""

    metric: str
    proxy: str
    paper_count: int
    mapping_record_count: int
    mean_confidence: str
    mean_confidence_weight: float
    mean_evidence_score: float
    quantitative_paper_count: int

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class EvidenceBundle:
    """All derived Evidence Engine results before serialization."""

    papers: tuple[PaperEvidence, ...]
    scores: tuple[EvidenceScore, ...]
    coverage: tuple[CoverageRow, ...]
    importance: tuple[ImportanceRow, ...]
    dependencies: tuple[DependencyRow, ...]
    matrix: tuple[Mapping[str, Any], ...]
    config: ScoringConfig
    input_paths: Mapping[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "scientific_scope": (
                "Evidence completeness and provenance assessment only. "
                "No simulation, biological inference, diagnosis, or calibration is performed."
            ),
            "input_paths": dict(self.input_paths),
            "config": self.config.as_dict(),
            "papers": [paper.as_dict() for paper in self.papers],
            "evidence_scores": [score.as_dict() for score in self.scores],
            "coverage": [row.as_dict() for row in self.coverage],
            "importance": [row.as_dict() for row in self.importance],
            "dependencies": [row.as_dict() for row in self.dependencies],
            "disease_layer_matrix": [dict(row) for row in self.matrix],
        }


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().casefold() in {"1", "true", "yes", "y"}


def resolve_path(path: str | Path) -> Path:
    """Return a normalized path without requiring it to exist."""

    return Path(path).expanduser()


__all__ = [
    "CONFIDENCE_WEIGHTS",
    "EXPECTED_PROXIES",
    "CoverageRow",
    "DependencyRow",
    "EvidenceBundle",
    "EvidenceCriterion",
    "EvidenceScore",
    "ImportanceRow",
    "MappingEvidence",
    "PaperEvidence",
    "ScoringConfig",
]
