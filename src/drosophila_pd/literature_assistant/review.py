"""Human review state for literature candidates."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

from .candidate import CandidatePhenotype
from .validation import validate_candidates


class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ReviewEntry:
    """Review metadata kept separately from candidate scientific fields."""

    status: ReviewStatus = ReviewStatus.PENDING
    comment: str = ""
    reviewer: str | None = None
    reviewed_at: str | None = None
    edited_fields: dict[str, Any] = field(default_factory=dict)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "comment": self.comment,
            "reviewer": self.reviewer,
            "reviewed_at": self.reviewed_at,
            "edited_fields": dict(self.edited_fields),
        }


class ReviewStore:
    """In-memory review store with explicit persistence to JSON."""

    schema_version = "1.0"

    def __init__(self, candidates: tuple[CandidatePhenotype, ...] | list[CandidatePhenotype] = ()) -> None:
        self._candidates: dict[str, CandidatePhenotype] = {}
        self._reviews: dict[str, ReviewEntry] = {}
        for candidate in candidates:
            self.add(candidate)

    @property
    def candidates(self) -> tuple[CandidatePhenotype, ...]:
        return tuple(self._candidates.values())

    def add(self, candidate: CandidatePhenotype) -> None:
        if candidate.candidate_id in self._candidates:
            raise ValueError(f"Duplicate candidate_id: {candidate.candidate_id}")
        self._candidates[candidate.candidate_id] = candidate
        self._reviews[candidate.candidate_id] = ReviewEntry()

    def get(self, candidate_id: str) -> CandidatePhenotype:
        try:
            return self._candidates[candidate_id]
        except KeyError as error:
            raise KeyError(f"Unknown candidate_id: {candidate_id}") from error

    def review_entry(self, candidate_id: str) -> ReviewEntry:
        self.get(candidate_id)
        return self._reviews[candidate_id]

    def review(
        self,
        candidate_id: str,
        status: ReviewStatus | str,
        *,
        reviewer: str,
        comment: str = "",
        reviewed_at: str | None = None,
    ) -> None:
        status = ReviewStatus(status)
        if status is ReviewStatus.PENDING:
            raise ValueError("A review action must approve or reject a candidate.")
        if not reviewer.strip():
            raise ValueError("reviewer must be non-empty.")
        if status is ReviewStatus.APPROVED:
            report = validate_candidates(self.candidates)["reports"][candidate_id]
            if not report["valid"]:
                raise ValueError(f"Candidate is not approvable: {report['issues']}")
        self._reviews[candidate_id] = ReviewEntry(
            status=status,
            comment=comment,
            reviewer=reviewer,
            reviewed_at=reviewed_at or _utc_now(),
            edited_fields=dict(self._reviews[candidate_id].edited_fields),
        )

    def approve(self, candidate_id: str, *, reviewer: str, comment: str = "", reviewed_at: str | None = None) -> None:
        self.review(candidate_id, ReviewStatus.APPROVED, reviewer=reviewer, comment=comment, reviewed_at=reviewed_at)

    def reject(self, candidate_id: str, *, reviewer: str, comment: str = "", reviewed_at: str | None = None) -> None:
        self.review(candidate_id, ReviewStatus.REJECTED, reviewer=reviewer, comment=comment, reviewed_at=reviewed_at)

    def edit(
        self,
        candidate_id: str,
        updates: Mapping[str, Any],
        *,
        reviewer: str,
        comment: str = "",
    ) -> CandidatePhenotype:
        if not reviewer.strip():
            raise ValueError("reviewer must be non-empty.")
        current = self.get(candidate_id)
        edited = current.with_updates(updates)
        self._candidates[candidate_id] = edited
        previous = self._reviews[candidate_id]
        self._reviews[candidate_id] = ReviewEntry(
            status=ReviewStatus.PENDING,
            comment=comment,
            reviewer=reviewer,
            reviewed_at=_utc_now(),
            edited_fields={**previous.edited_fields, **dict(updates)},
        )
        return edited

    def approved_records(self) -> tuple[Any, ...]:
        return tuple(
            self._candidates[candidate_id].to_phenotype_record()
            for candidate_id, entry in self._reviews.items()
            if entry.status is ReviewStatus.APPROVED
        )

    def status_for(self, candidate_id: str) -> ReviewStatus:
        return self.review_entry(candidate_id).status

    def to_mapping(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "scientific_scope": "Candidate observations require human review; no automatic inference.",
            "candidates": [candidate.to_mapping() for candidate in self.candidates],
            "reviews": {candidate_id: entry.to_mapping() for candidate_id, entry in self._reviews.items()},
        }

    def write_json(self, path: str | Path) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(self.to_mapping(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return destination


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


__all__ = ["ReviewEntry", "ReviewStatus", "ReviewStore"]
