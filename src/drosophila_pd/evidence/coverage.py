"""Coverage summaries for Disease Layer proxy evidence."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Mapping

from .models import CoverageRow, EvidenceScore, MappingEvidence, PaperEvidence, ScoringConfig


def compute_coverage(
    papers: Iterable[PaperEvidence],
    scores: Iterable[EvidenceScore],
    config: ScoringConfig,
) -> tuple[CoverageRow, ...]:
    """Count paper and quantitative coverage for every configured proxy."""

    paper_list = tuple(papers)
    score_by_id = {score.paper_id: score for score in scores}
    mappings_by_proxy: dict[str, list[tuple[str, MappingEvidence]]] = defaultdict(list)
    for paper in paper_list:
        for mapping in paper.mappings:
            if mapping.disease_layer_proxy in config.expected_proxies:
                mappings_by_proxy[mapping.disease_layer_proxy].append((paper.paper_id, mapping))

    rows = []
    for proxy in config.expected_proxies:
        entries = mappings_by_proxy.get(proxy, [])
        paper_ids = {paper_id for paper_id, _ in entries}
        quantitative = {
            paper_id for paper_id in paper_ids if score_by_id.get(paper_id) and score_by_id[paper_id].quantitative_metric
        }
        calibration = {
            paper_id for paper_id, mapping in entries if _candidate(mapping.calibration_candidate)
        }
        validation = {
            paper_id for paper_id, mapping in entries if _candidate(mapping.validation_candidate)
        }
        if not paper_ids:
            status = "no_literature"
        elif quantitative:
            status = "quantitative_coverage"
        else:
            status = "qualitative_only"
        rows.append(
            CoverageRow(
                proxy=proxy,
                paper_count=len(paper_ids),
                mapping_record_count=len(entries),
                quantitative_paper_count=len(quantitative),
                qualitative_paper_count=len(paper_ids - quantitative),
                calibration_candidate_count=len(calibration),
                validation_candidate_count=len(validation),
                coverage_status=status,
            )
        )
    return tuple(rows)


def _candidate(value: str) -> bool:
    return str(value).strip().casefold() in {"true", "yes", "1", "conditional"}


__all__ = ["compute_coverage"]
