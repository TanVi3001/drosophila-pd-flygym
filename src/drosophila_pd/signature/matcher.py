"""Rank simulation signatures against a literature signature."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .distance import (
    DistanceResult,
    cosine_distance,
    dynamic_time_warping_distance,
    earth_mover_distance,
    euclidean_distance,
    mahalanobis_distance,
    weighted_euclidean_distance,
)
from .normalization import normalize_signatures
from .signature import DiseaseSignature


@dataclass(frozen=True)
class MatchResult:
    """One ranked comparison, with a computational similarity only."""

    signature_id: str
    distance: DistanceResult
    similarity: float | None
    rank: int | None = None

    def to_mapping(self) -> dict[str, Any]:
        return {
            "signature_id": self.signature_id,
            "distance": self.distance.to_mapping(),
            "similarity": self.similarity,
            "rank": self.rank,
        }


@dataclass(frozen=True)
class MatchingReport:
    """Complete literature-to-simulation comparison."""

    literature_id: str
    distance_method: str
    normalization_method: str
    results: tuple[MatchResult, ...]

    @property
    def ranking(self) -> tuple[MatchResult, ...]:
        return tuple(sorted((item for item in self.results if item.rank is not None), key=lambda item: int(item.rank)))

    def to_mapping(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "literature_signature": self.literature_id,
            "distance_method": self.distance_method,
            "normalization_method": self.normalization_method,
            "scientific_scope": (
                "Computational signature distance and ranking only; similarity is not "
                "medical interpretation, disease stage, or biological severity."
            ),
            "results": [item.to_mapping() for item in self.results],
            "ranking": [item.to_mapping() for item in self.ranking],
        }


class SignatureMatcher:
    """Matcher with no optimizer and no simulation execution."""

    def __init__(self, *, distance_method: str = "euclidean", normalization_method: str = "none") -> None:
        self.distance_method = distance_method
        self.normalization_method = normalization_method

    def match(
        self,
        literature: DiseaseSignature,
        simulations: Iterable[DiseaseSignature],
        *,
        weights: Mapping[str, float] | None = None,
        healthy_baseline: DiseaseSignature | None = None,
    ) -> MatchingReport:
        candidates = tuple(simulations)
        normalized = normalize_signatures(
            (literature, *candidates),
            method=self.normalization_method,
            healthy_baseline=healthy_baseline,
        )
        normalized_literature = normalized[0].signature
        comparisons: list[MatchResult] = []
        for candidate, normalized_candidate in zip(candidates, normalized[1:]):
            distance = _calculate_distance(
                normalized_literature,
                normalized_candidate.signature,
                method=self.distance_method,
                weights=weights,
            )
            comparisons.append(
                MatchResult(
                    signature_id=candidate.signature_id or "unidentified",
                    distance=distance,
                    similarity=_similarity(distance),
                )
            )
        ranked_indices = [index for index, result in enumerate(comparisons) if result.distance.available]
        ranked_indices.sort(key=lambda index: float(comparisons[index].distance.distance))
        ranks = {index: rank for rank, index in enumerate(ranked_indices, start=1)}
        ranked = tuple(
            MatchResult(
                signature_id=result.signature_id,
                distance=result.distance,
                similarity=result.similarity,
                rank=ranks.get(index),
            )
            for index, result in enumerate(comparisons)
        )
        return MatchingReport(
            literature_id=literature.signature_id or "unidentified",
            distance_method=self.distance_method,
            normalization_method=self.normalization_method,
            results=ranked,
        )


def match_signatures(
    literature: DiseaseSignature,
    simulations: Iterable[DiseaseSignature],
    *,
    distance_method: str = "euclidean",
    normalization_method: str = "none",
    weights: Mapping[str, float] | None = None,
    healthy_baseline: DiseaseSignature | None = None,
) -> MatchingReport:
    return SignatureMatcher(
        distance_method=distance_method,
        normalization_method=normalization_method,
    ).match(literature, simulations, weights=weights, healthy_baseline=healthy_baseline)


def _calculate_distance(first: DiseaseSignature, second: DiseaseSignature, *, method: str, weights: Mapping[str, float] | None) -> DistanceResult:
    method = method.lower().replace("-", "_")
    if method == "euclidean":
        return euclidean_distance(first, second)
    if method in {"weighted_euclidean", "weighted"}:
        if weights is None:
            return DistanceResult(method, None, "UNAVAILABLE", reason="Weighted Euclidean requires explicit weights.")
        return weighted_euclidean_distance(first, second, weights=weights)
    if method == "cosine":
        return cosine_distance(first, second)
    if method == "mahalanobis":
        return mahalanobis_distance(first, second)
    if method in {"dtw", "dynamic_time_warping"}:
        return dynamic_time_warping_distance(first, second)
    if method in {"earth_mover", "emd", "earth_mover_distance"}:
        return earth_mover_distance(first, second)
    raise ValueError(f"Unsupported distance method: {method}")


def _similarity(distance: DistanceResult) -> float | None:
    if not distance.available:
        return None
    return 1.0 / (1.0 + float(distance.distance))


__all__ = ["MatchResult", "MatchingReport", "SignatureMatcher", "match_signatures"]
