"""Evidence-presence ranking for Disease Layer proxies."""

from __future__ import annotations

from .models import CoverageRow, EvidenceScore, ImportanceRow, MappingEvidence, PaperEvidence, ScoringConfig


def rank_proxy_importance(
    papers: tuple[PaperEvidence, ...] | list[PaperEvidence],
    scores: tuple[EvidenceScore, ...] | list[EvidenceScore],
    coverage: tuple[CoverageRow, ...] | list[CoverageRow],
    config: ScoringConfig,
) -> tuple[ImportanceRow, ...]:
    """Rank proxies by the sum of evidence-completeness scores.

    This is a literature coverage ranking, not a biological importance score.
    """

    score_by_id = {score.paper_id: score for score in scores}
    coverage_by_proxy = {row.proxy: row for row in coverage}
    totals = {proxy: [] for proxy in config.expected_proxies}
    for paper in papers:
        for proxy in {mapping.disease_layer_proxy for mapping in paper.mappings}:
            if proxy in totals and paper.paper_id in score_by_id:
                totals[proxy].append(score_by_id[paper.paper_id].score)

    ordered = sorted(
        config.expected_proxies,
        key=lambda proxy: (-sum(totals[proxy]), -len(totals[proxy]), config.expected_proxies.index(proxy)),
    )
    rows = []
    for rank, proxy in enumerate(ordered, start=1):
        values = totals[proxy]
        rows.append(
            ImportanceRow(
                rank=rank,
                proxy=proxy,
                paper_count=len(values),
                total_evidence_score=round(sum(values), 6),
                mean_evidence_score=round(sum(values) / len(values), 6) if values else 0.0,
                quantitative_paper_count=sum(
                    1 for paper_id in _paper_ids_for_proxy(papers, proxy) if score_by_id.get(paper_id, None) and score_by_id[paper_id].quantitative_metric
                ),
                coverage_status=coverage_by_proxy[proxy].coverage_status,
            )
        )
    return tuple(rows)


def _paper_ids_for_proxy(papers: tuple[PaperEvidence, ...] | list[PaperEvidence], proxy: str) -> set[str]:
    return {
        paper.paper_id
        for paper in papers
        if any(mapping.disease_layer_proxy == proxy for mapping in paper.mappings)
    }


__all__ = ["rank_proxy_importance"]
