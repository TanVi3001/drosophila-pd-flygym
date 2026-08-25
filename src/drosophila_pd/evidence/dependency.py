"""Metric-to-Disease-Layer dependency summaries."""

from __future__ import annotations

from collections import defaultdict

from .models import DependencyRow, EvidenceScore, PaperEvidence


def build_dependency_rows(
    papers: tuple[PaperEvidence, ...] | list[PaperEvidence],
    scores: tuple[EvidenceScore, ...] | list[EvidenceScore],
) -> tuple[DependencyRow, ...]:
    """Aggregate mapping rows by metric and proxy without causal inference."""

    score_by_id = {score.paper_id: score for score in scores}
    groups: dict[tuple[str, str], list[tuple[str, object]]] = defaultdict(list)
    for paper in papers:
        for mapping in paper.mappings:
            if not mapping.metric or not mapping.disease_layer_proxy or mapping.disease_layer_proxy == "UNMAPPED":
                continue
            groups[(mapping.metric, mapping.disease_layer_proxy)].append((paper.paper_id, mapping))

    rows = []
    for (metric, proxy), entries in sorted(groups.items()):
        weights = [mapping.confidence_weight for _, mapping in entries]
        paper_ids = {paper_id for paper_id, _ in entries}
        evidence_values = [score_by_id[paper_id].score for paper_id in paper_ids if paper_id in score_by_id]
        quantitative = {
            paper_id for paper_id in paper_ids if score_by_id.get(paper_id) and score_by_id[paper_id].quantitative_metric
        }
        mean_weight = sum(weights) / len(weights) if weights else 0.0
        rows.append(
            DependencyRow(
                metric=metric,
                proxy=proxy,
                paper_count=len(paper_ids),
                mapping_record_count=len(entries),
                mean_confidence=_confidence_label(mean_weight),
                mean_confidence_weight=round(mean_weight, 6),
                mean_evidence_score=round(sum(evidence_values) / len(evidence_values), 6) if evidence_values else 0.0,
                quantitative_paper_count=len(quantitative),
            )
        )
    return tuple(rows)


def build_disease_layer_matrix(
    dependencies: tuple[DependencyRow, ...] | list[DependencyRow],
    expected_proxies: tuple[str, ...],
) -> tuple[dict[str, object], ...]:
    """Build a metric-row matrix of confidence-adjusted evidence support.

    Each cell is ``mean evidence score * mean confidence weight / 100``. Empty
    cells mean that no mapping record was supplied, not zero biological effect.
    """

    metrics = sorted({row.metric for row in dependencies if row.metric})
    rows = []
    for metric in metrics:
        row: dict[str, object] = {"metric": metric}
        for proxy in expected_proxies:
            matches = [item for item in dependencies if item.metric == metric and item.proxy == proxy]
            row[proxy] = round(matches[0].mean_evidence_score * matches[0].mean_confidence_weight / 100, 6) if matches else ""
        rows.append(row)
    return tuple(rows)


def _confidence_label(value: float) -> str:
    if value >= 0.8:
        return "HIGH"
    if value >= 0.5:
        return "MEDIUM"
    if value > 0:
        return "LOW"
    return "NONE"


__all__ = ["build_dependency_rows", "build_disease_layer_matrix"]
