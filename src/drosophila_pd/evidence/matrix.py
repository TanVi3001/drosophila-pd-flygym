"""Matrix-facing helpers for Evidence Engine outputs."""

from __future__ import annotations

from .dependency import build_disease_layer_matrix, build_dependency_rows
from .models import DependencyRow, EvidenceScore, PaperEvidence


def build_matrices(
    papers: tuple[PaperEvidence, ...] | list[PaperEvidence],
    scores: tuple[EvidenceScore, ...] | list[EvidenceScore],
    expected_proxies: tuple[str, ...],
) -> tuple[tuple[DependencyRow, ...], tuple[dict[str, object], ...]]:
    """Return detailed dependency rows and the metric-by-proxy matrix."""

    dependencies = build_dependency_rows(papers, scores)
    return dependencies, build_disease_layer_matrix(dependencies, expected_proxies)


__all__ = ["build_disease_layer_matrix", "build_dependency_rows", "build_matrices"]
