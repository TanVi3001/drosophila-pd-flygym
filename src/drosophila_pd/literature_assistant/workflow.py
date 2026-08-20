"""Orchestration for local literature curation and explicit human review."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

from .candidate import CandidatePhenotype
from .parser import parse_source
from .report import write_review_reports
from .review import ReviewStore, ReviewStatus


@dataclass
class LiteratureAssistantWorkflow:
    """Manage a review queue without modifying the phenotype database."""

    output_dir: Path | str
    store: ReviewStore = field(default_factory=ReviewStore)

    def __post_init__(self) -> None:
        self.output_dir = Path(self.output_dir)

    @property
    def review_path(self) -> Path:
        return self.output_dir / "candidate_review.json"

    def collect(self, sources: Iterable[str | Path]) -> tuple[CandidatePhenotype, ...]:
        collected: list[CandidatePhenotype] = []
        for source in sources:
            for candidate in parse_source(source):
                self.store.add(candidate)
                collected.append(candidate)
        self.persist()
        return tuple(collected)

    def persist(self) -> Path:
        return self.store.write_json(self.review_path)

    def edit(self, candidate_id: str, updates: Mapping[str, Any], *, reviewer: str, comment: str = "") -> None:
        self.store.edit(candidate_id, updates, reviewer=reviewer, comment=comment)
        self.persist()

    def approve(self, candidate_id: str, *, reviewer: str, comment: str = "") -> None:
        self.store.approve(candidate_id, reviewer=reviewer, comment=comment)
        self.persist()

    def reject(self, candidate_id: str, *, reviewer: str, comment: str = "") -> None:
        self.store.reject(candidate_id, reviewer=reviewer, comment=comment)
        self.persist()

    def export_approved(self) -> tuple[Any, ...]:
        """Export only explicitly approved candidates as existing atlas records."""

        self.persist()
        return self.store.approved_records()

    def write_reports(self) -> dict[str, Path]:
        self.persist()
        return write_review_reports(self.store, self.output_dir)

    def run(self, sources: Iterable[str | Path]) -> dict[str, Path]:
        """Collect sources and write the pending review artifacts.

        Parsing never changes status automatically; all candidates remain
        pending until a human calls ``approve`` or ``reject``.
        """

        self.collect(sources)
        return self.write_reports()

    def status_counts(self) -> dict[str, int]:
        counts = {status.value: 0 for status in ReviewStatus}
        for candidate in self.store.candidates:
            counts[self.store.status_for(candidate.candidate_id).value] += 1
        return counts


__all__ = ["LiteratureAssistantWorkflow"]
