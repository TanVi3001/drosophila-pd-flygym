"""Configurable evidence completeness scoring."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

from .models import EvidenceCriterion, EvidenceScore, PaperEvidence, ScoringConfig


SUPPORTED_CRITERIA = (
    "locomotion_assay",
    "quantitative_metric",
    "sample_size",
    "protocol",
    "genotype",
    "control",
    "provenance",
    "doi_pmid",
    "supplementary",
)


def default_scoring_config() -> ScoringConfig:
    """Return the default policy; weights remain replaceable by callers."""

    descriptions = {
        "locomotion_assay": "A named locomotion, climbing, flight, crawling, geotaxis or trajectory assay is present.",
        "quantitative_metric": "A numeric phenotype value or source-data value is available.",
        "sample_size": "Sample size or the number of experimental units is reported.",
        "protocol": "The assay protocol contains enough method detail to reproduce the measurement.",
        "genotype": "The genotype/model is identified.",
        "control": "A control, revertant, wild-type or comparison group is identified.",
        "provenance": "A source URL or equivalent provenance is recorded.",
        "doi_pmid": "A DOI or PMID is recorded.",
        "supplementary": "Supplementary material or source-data provenance is recorded.",
    }
    weights = {
        "locomotion_assay": 18.0,
        "quantitative_metric": 18.0,
        "sample_size": 12.0,
        "protocol": 12.0,
        "genotype": 10.0,
        "control": 10.0,
        "provenance": 10.0,
        "doi_pmid": 5.0,
        "supplementary": 5.0,
    }
    return ScoringConfig(
        criteria=tuple(
            EvidenceCriterion(name=name, weight=weights[name], description=descriptions[name])
            for name in SUPPORTED_CRITERIA
        )
    )


def load_scoring_config(config: str | Path | Mapping[str, Any] | ScoringConfig | None = None) -> ScoringConfig:
    """Load a scoring policy from YAML/JSON, mapping, or defaults."""

    if config is None:
        return default_scoring_config()
    if isinstance(config, ScoringConfig):
        return config
    if isinstance(config, (str, Path)):
        path = Path(config)
        payload = json.loads(path.read_text(encoding="utf-8")) if path.suffix.lower() == ".json" else yaml.safe_load(path.read_text(encoding="utf-8"))
    else:
        payload = dict(config)
    if not isinstance(payload, Mapping):
        raise ValueError("evidence scoring config must be a mapping")

    defaults = default_scoring_config()
    configured = payload.get("criteria", payload.get("weights", {}))
    if isinstance(configured, Mapping):
        criteria = []
        for default in defaults.criteria:
            value = configured.get(default.name, default.weight)
            criteria.append(
                EvidenceCriterion(
                    name=default.name,
                    weight=float(value),
                    description=default.description,
                )
            )
    elif isinstance(configured, Sequence) and not isinstance(configured, (str, bytes)):
        criteria = []
        for item in configured:
            if not isinstance(item, Mapping):
                raise ValueError("each evidence criterion must be a mapping")
            name = str(item.get("name", "")).strip()
            if name not in SUPPORTED_CRITERIA:
                raise ValueError(f"unsupported evidence criterion: {name}")
            criteria.append(
                EvidenceCriterion(
                    name=name,
                    weight=float(item.get("weight", 0)),
                    description=str(item.get("description", "")),
                )
            )
    else:
        raise ValueError("criteria must be a mapping or a list")
    names = {criterion.name for criterion in criteria}
    if not names:
        raise ValueError("scoring config contains no criteria")
    return ScoringConfig(
        criteria=tuple(criteria),
        expected_proxies=tuple(payload.get("expected_proxies", defaults.expected_proxies)),
        high_threshold=float(payload.get("high_threshold", defaults.high_threshold)),
        medium_threshold=float(payload.get("medium_threshold", defaults.medium_threshold)),
    )


def score_paper(paper: PaperEvidence, config: ScoringConfig | None = None) -> EvidenceScore:
    """Score evidence completeness for one joined paper record."""

    policy = load_scoring_config(config)
    criteria = {criterion.name: float(_criterion_value(paper, criterion.name)) for criterion in policy.criteria}
    total_weight = policy.total_weight
    weighted = {
        name: value * next(item.weight for item in policy.criteria if item.name == name)
        for name, value in criteria.items()
    }
    score = 100.0 * sum(weighted.values()) / total_weight if total_weight else 0.0
    quantitative = bool(_criterion_value(paper, "quantitative_metric"))
    protocol = bool(_criterion_value(paper, "protocol"))
    sample_size = bool(_criterion_value(paper, "sample_size"))
    calibration = any(_is_candidate(mapping.calibration_candidate) for mapping in paper.mappings)
    validation = any(_is_candidate(mapping.validation_candidate) for mapping in paper.mappings)
    proxies = tuple(sorted({mapping.disease_layer_proxy for mapping in paper.mappings if mapping.disease_layer_proxy and mapping.disease_layer_proxy != "UNMAPPED"}))
    notes = []
    if not quantitative:
        notes.append("No verified quantitative phenotype value is available.")
    if any(mapping.manual_review_required for mapping in paper.mappings):
        notes.append("Manual review is required before calibration use.")
    return EvidenceScore(
        paper_id=paper.paper_id,
        score=round(score, 6),
        level=policy.level_for(score),
        criteria=criteria,
        weighted_criteria={name: round(value, 6) for name, value in weighted.items()},
        quantitative_metric=quantitative,
        protocol_available=protocol,
        sample_size_available=sample_size,
        calibration_candidate=calibration,
        validation_candidate=validation,
        proxy_names=proxies,
        mapping_count=len(paper.mappings),
        manual_review_required=any(mapping.manual_review_required for mapping in paper.mappings),
        notes=tuple(notes),
    )


def score_papers(papers: Sequence[PaperEvidence], config: ScoringConfig | None = None) -> tuple[EvidenceScore, ...]:
    """Score all papers in stable input order."""

    policy = load_scoring_config(config)
    return tuple(score_paper(paper, policy) for paper in papers)


def _criterion_value(paper: PaperEvidence, name: str) -> bool:
    candidate = paper.candidate
    metadata = paper.paper
    combined = " ".join(
        _text(value)
        for value in (
            candidate,
            metadata,
            [mapping.as_dict() for mapping in paper.mappings],
        )
    ).casefold()
    if name == "locomotion_assay":
        assay_text = " ".join(
            [
                str(candidate.get("locomotion_assay", "")),
                _text(metadata.get("assays", "")),
                " ".join(mapping.metric for mapping in paper.mappings),
            ]
        ).casefold()
        if any(marker in assay_text for marker in ("not verified", "not confirmed", "pending full text", "exact assay to verify", "not the central endpoint", "requires confirmation")):
            return any(marker in assay_text for marker in ("climbing", "negative geotaxis", "flight assay", "crawling", "trajectory", "walking assay", "walking speed", "sing"))
        return any(marker in assay_text for marker in ("climbing", "negative geotaxis", "flight", "crawling", "trajectory", "walking", "geotaxis", "locomotion", "movement", "speed", "idling"))
    if name == "quantitative_metric":
        values = metadata.get("numeric_values")
        measurement_text = str(candidate.get("phenotype_measurements", ""))
        return bool(values) or bool(
            re.search(
                r"\b(?:speed|distance|time|duration|frequency|stride|climbing|turning|activity|pause|value)\b\D{0,20}\d"
                r"|\d+(?:\.\d+)?\s*(?:mm/s|mm|cm/s|s|ms|hz|%|percent)\b",
                measurement_text,
                flags=re.IGNORECASE,
            )
        )
    if name == "sample_size":
        sample_text = " ".join(str(metadata.get(key, "")) for key in ("sample_size", "age_sex"))
        sample_text += " " + str(candidate.get("age_sex_sample", ""))
        return bool(re.search(r"(?:\bn\s*[=><]|\bn\s*≥|\bN\s*[=><]|sample|animals?|flies?|flies/genotype|trials?|experiments?)", sample_text, flags=re.IGNORECASE))
    if name == "protocol":
        protocol_text = " ".join(str(metadata.get(key, "")) for key in ("assays", "age_sex", "sample_size", "figure_table_source"))
        protocol_text += " " + " ".join(str(candidate.get(key, "")) for key in ("locomotion_assay", "age_sex_sample", "phenotype_measurements"))
        return bool(_criterion_value(paper, "locomotion_assay")) and bool(re.search(r"(?:cm|sec|second|minute|trial|vial|finish|line|day|temperature|method|assay|n\s*=)", protocol_text, flags=re.IGNORECASE))
    if name == "genotype":
        return bool(re.search(r"\bpink1\b|\bPINK1\b|genotype|mutant|RNAi|knockdown|knock-in", combined, flags=re.IGNORECASE))
    if name == "control":
        return bool(re.search(r"control|revertant|\bRV\b|wild[- ]type|\bWT\b|\+/\+|comparison group|healthy", combined, flags=re.IGNORECASE))
    if name == "provenance":
        return bool(metadata.get("article_url") or candidate.get("article_url") or metadata.get("open_access_url"))
    if name == "doi_pmid":
        return bool(str(metadata.get("doi", "")).strip() or str(metadata.get("pmid", "")).strip() or str(candidate.get("doi", "")).strip() or str(candidate.get("pmid", "")).strip())
    if name == "supplementary":
        return bool(re.search(r"supplement|source[- ]data|supplementary", combined, flags=re.IGNORECASE))
    raise ValueError(f"unsupported evidence criterion: {name}")


def _is_candidate(value: str) -> bool:
    return str(value).strip().casefold() in {"true", "yes", "1", "conditional"}


def _text(value: Any) -> str:
    if isinstance(value, Mapping):
        return " ".join(f"{key} {_text(item)}" for key, item in value.items())
    if isinstance(value, (list, tuple, set)):
        return " ".join(_text(item) for item in value)
    return str(value)


__all__ = [
    "SUPPORTED_CRITERIA",
    "default_scoring_config",
    "load_scoring_config",
    "score_paper",
    "score_papers",
]
