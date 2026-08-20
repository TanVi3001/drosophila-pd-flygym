"""File-driven calibration engine; simulation execution remains external."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from drosophila_pd.parkinson.phenotype_database import PhenotypeTarget

from .objective_functions import ObjectiveFunction, ObjectiveResult


@dataclass(frozen=True)
class CalibrationCandidate:
    candidate_id: str
    parameters: dict[str, Any]
    metrics: dict[str, Any]
    objective: ObjectiveResult

    def to_mapping(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "parameters": dict(self.parameters),
            "metrics": dict(self.metrics),
            "objective": self.objective.to_mapping(),
        }


@dataclass(frozen=True)
class CalibrationRun:
    status: str
    objective_method: str
    target_count: int
    numeric_target_count: int
    candidate_count: int
    candidates: tuple[CalibrationCandidate, ...]
    best_candidate_id: str | None
    provenance: dict[str, Any]

    @property
    def ranked_candidates(self) -> tuple[CalibrationCandidate, ...]:
        return tuple(
            sorted(
                (item for item in self.candidates if item.objective.loss is not None),
                key=lambda item: item.objective.loss,
            )
        )

    @property
    def best_candidate(self) -> CalibrationCandidate | None:
        if self.best_candidate_id is None:
            return None
        return next(
            (item for item in self.candidates if item.candidate_id == self.best_candidate_id),
            None,
        )

    def to_mapping(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "objective_method": self.objective_method,
            "target_count": self.target_count,
            "numeric_target_count": self.numeric_target_count,
            "candidate_count": self.candidate_count,
            "best_candidate_id": self.best_candidate_id,
            "candidates": [item.to_mapping() for item in self.candidates],
            "provenance": dict(self.provenance),
            "scientific_scope": (
                "This is literature-constrained computational phenotype scoring. "
                "It is not a biological Parkinson model or clinical validation."
            ),
        }


class CalibrationEngine:
    """Score supplied metrics without running or mutating a simulation."""

    def __init__(
        self,
        targets: Iterable[PhenotypeTarget],
        *,
        objective: ObjectiveFunction | None = None,
        provenance: Mapping[str, Any] | None = None,
    ) -> None:
        self.targets = tuple(targets)
        self.objective = objective or ObjectiveFunction()
        self.provenance = dict(provenance or {})

    def evaluate_candidate(
        self,
        candidate_id: str,
        parameters: Mapping[str, Any],
        metrics: Mapping[str, Any],
    ) -> CalibrationCandidate:
        if not str(candidate_id).strip():
            raise ValueError("candidate_id must be non-empty.")
        return CalibrationCandidate(
            candidate_id=str(candidate_id),
            parameters=dict(parameters),
            metrics=dict(metrics),
            objective=self.objective.evaluate(metrics, self.targets),
        )

    def evaluate_candidates(
        self,
        candidates: Iterable[Mapping[str, Any]],
    ) -> CalibrationRun:
        evaluated: list[CalibrationCandidate] = []
        seen: set[str] = set()
        for item in candidates:
            candidate_id = str(item.get("candidate_id", item.get("id", ""))).strip()
            if not candidate_id:
                raise ValueError("Each candidate requires candidate_id or id.")
            if candidate_id in seen:
                raise ValueError(f"Duplicate candidate_id: {candidate_id}")
            seen.add(candidate_id)
            parameters = item.get("parameters", {})
            metrics = item.get("metrics", item.get("derived_locomotion_metrics", {}))
            if not isinstance(parameters, Mapping) or not isinstance(metrics, Mapping):
                raise ValueError(f"Candidate {candidate_id!r} parameters and metrics must be mappings.")
            evaluated.append(self.evaluate_candidate(candidate_id, parameters, metrics))

        numeric_target_count = sum(target.numeric for target in self.targets)
        best = min(
            (
                item
                for item in evaluated
                if item.objective.status == "PASS" and item.objective.loss is not None
            ),
            key=lambda item: item.objective.loss,
            default=None,
        )
        if not numeric_target_count:
            status = "UNAVAILABLE_NUMERIC_TARGET"
        elif not evaluated:
            status = "NO_CANDIDATES"
        elif best is None:
            status = "FAILED_NO_COMPLETE_CANDIDATE"
        else:
            status = "PASS"
        provenance = {
            "created_at_utc": datetime.now(UTC).isoformat(),
            "simulation_executed_by_engine": False,
            "objective": {
                "method": self.objective.method,
                "normalize": self.objective.normalize,
                "missing_policy": self.objective.missing_policy,
            },
            **self.provenance,
        }
        return CalibrationRun(
            status=status,
            objective_method=self.objective.method,
            target_count=len(self.targets),
            numeric_target_count=numeric_target_count,
            candidate_count=len(evaluated),
            candidates=tuple(evaluated),
            best_candidate_id=None if best is None else best.candidate_id,
            provenance=provenance,
        )


def load_simulation_metrics(path: str | Path) -> tuple[dict[str, Any], ...]:
    """Load archived metrics in direct, wrapped, or candidate-list form."""

    source = Path(path)
    with source.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        raw_candidates = payload
    elif isinstance(payload, dict) and isinstance(payload.get("candidates"), list):
        raw_candidates = payload["candidates"]
    else:
        raw_candidates = [payload]

    candidates: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_candidates):
        if not isinstance(raw, Mapping):
            raise ValueError(f"Metrics candidate {index} must be a JSON object.")
        metrics = raw.get("metrics", raw.get("derived_locomotion_metrics", raw))
        if not isinstance(metrics, Mapping):
            raise ValueError(f"Metrics candidate {index} must contain a mapping.")
        candidate_id = raw.get("candidate_id", raw.get("id", f"candidate_{index + 1:03d}"))
        parameters = raw.get("parameters", {})
        if not isinstance(parameters, Mapping):
            raise ValueError(f"Metrics candidate {index} parameters must be a mapping.")
        candidates.append(
            {
                "candidate_id": str(candidate_id),
                "parameters": dict(parameters),
                "metrics": dict(metrics),
            }
        )
    return tuple(candidates)


__all__ = [
    "CalibrationCandidate",
    "CalibrationEngine",
    "CalibrationRun",
    "load_simulation_metrics",
]
