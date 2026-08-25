"""Validation and loading for Evidence Engine curation inputs."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping

from .models import MappingEvidence, PaperEvidence, ScoringConfig


class EvidenceValidationError(ValueError):
    """Raised when curation inputs cannot be joined safely."""


def load_evidence_inputs(
    mapping_csv: str | Path,
    paper_information_json: str | Path,
    candidate_review_csv: str | Path,
    config: ScoringConfig | None = None,
) -> tuple[PaperEvidence, ...]:
    """Load and join the three curation artifacts by ``paper_id``."""

    paths = {
        "mapping_csv": Path(mapping_csv),
        "paper_information_json": Path(paper_information_json),
        "candidate_review_csv": Path(candidate_review_csv),
    }
    missing = [f"{name}: {path}" for name, path in paths.items() if not path.is_file()]
    if missing:
        raise EvidenceValidationError("missing evidence input file(s): " + "; ".join(missing))

    mapping_rows = _read_csv(paths["mapping_csv"], "mapping_csv")
    candidate_rows = _read_csv(paths["candidate_review_csv"], "candidate_review_csv")
    try:
        paper_payload = json.loads(paths["paper_information_json"].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceValidationError(f"cannot read paper information JSON: {paths['paper_information_json']}: {exc}") from exc
    paper_rows = paper_payload.get("papers") if isinstance(paper_payload, Mapping) else None
    if not isinstance(paper_rows, list):
        raise EvidenceValidationError("paper_information.json must contain a 'papers' list")

    candidates = _index_rows(candidate_rows, "candidate_review.csv")
    papers = _index_json_rows(paper_rows)
    mappings: dict[str, list[MappingEvidence]] = {}
    seen_mapping_keys: set[tuple[str, str, str, str]] = set()
    for raw in mapping_rows:
        mapping = MappingEvidence.from_row(raw)
        key = (mapping.paper_id, mapping.phenotype, mapping.metric, mapping.disease_layer_proxy)
        if key in seen_mapping_keys:
            raise EvidenceValidationError(f"duplicate disease-layer mapping row: {key}")
        seen_mapping_keys.add(key)
        mappings.setdefault(mapping.paper_id, []).append(mapping)

    candidate_ids = set(candidates)
    paper_ids = set(papers)
    if candidate_ids != paper_ids:
        raise EvidenceValidationError(
            "candidate_review.csv and paper_information.json paper IDs differ: "
            f"candidate_only={sorted(candidate_ids - paper_ids)}, paper_only={sorted(paper_ids - candidate_ids)}"
        )
    unknown_mapping_ids = sorted(set(mappings) - candidate_ids)
    if unknown_mapping_ids:
        raise EvidenceValidationError("mapping references unknown paper_id(s): " + ", ".join(unknown_mapping_ids))

    records = tuple(
        PaperEvidence(
            paper_id=paper_id,
            paper=papers[paper_id],
            candidate=candidates[paper_id],
            mappings=tuple(mappings.get(paper_id, ())),
        )
        for paper_id in sorted(candidate_ids)
    )
    validate_loaded_inputs(records, config=config)
    return records


def validate_loaded_inputs(
    papers: tuple[PaperEvidence, ...] | list[PaperEvidence],
    config: ScoringConfig | None = None,
) -> tuple[str, ...]:
    """Validate already-joined records and return non-fatal informational notes."""

    expected = set(config.expected_proxies) if config else None
    if not papers:
        raise EvidenceValidationError("evidence inputs contain no papers")
    notes: list[str] = []
    for paper in papers:
        if not paper.paper_id:
            raise EvidenceValidationError("paper_id must not be empty")
        if not paper.mappings:
            notes.append(f"paper has no disease-layer mapping: {paper.paper_id}")
        for mapping in paper.mappings:
            if expected is not None and mapping.disease_layer_proxy not in expected and mapping.disease_layer_proxy != "UNMAPPED":
                raise EvidenceValidationError(
                    f"unsupported proxy '{mapping.disease_layer_proxy}' in paper {paper.paper_id}"
                )
    return tuple(notes)


def _read_csv(path: Path, label: str) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
    except (OSError, csv.Error) as exc:
        raise EvidenceValidationError(f"cannot read {label}: {path}: {exc}") from exc
    if not rows or not rows[0]:
        raise EvidenceValidationError(f"{label} is empty: {path}")
    return rows


def _index_rows(rows: list[dict[str, str]], label: str) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        paper_id = str(row.get("paper_id", "")).strip()
        if not paper_id:
            raise EvidenceValidationError(f"{label} contains a row without paper_id")
        if paper_id in indexed:
            raise EvidenceValidationError(f"{label} contains duplicate paper_id: {paper_id}")
        indexed[paper_id] = row
    return indexed


def _index_json_rows(rows: list[Any]) -> dict[str, Mapping[str, Any]]:
    indexed: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise EvidenceValidationError("each paper_information.json papers item must be an object")
        paper_id = str(row.get("paper_id", "")).strip()
        if not paper_id:
            raise EvidenceValidationError("paper_information.json contains a paper without paper_id")
        if paper_id in indexed:
            raise EvidenceValidationError(f"paper_information.json contains duplicate paper_id: {paper_id}")
        indexed[paper_id] = row
    return indexed


__all__ = [
    "EvidenceValidationError",
    "load_evidence_inputs",
    "validate_loaded_inputs",
]
