"""Deterministic, literature-constrained calibration utilities.

The engine is intentionally runner-agnostic.  A caller supplies an evaluator
that runs an existing experiment and returns named metrics; this module only
enumerates parameter candidates, scores available numeric targets, and records
provenance.  No simulation or biological inference is performed here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import itertools
import math
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence
import json

from .phenotype_database import PhenotypeTarget


MetricEvaluator = Callable[[Mapping[str, float]], Mapping[str, Any]]


class CalibrationError(ValueError):
    """Raised when a calibration configuration cannot be evaluated."""


@dataclass(frozen=True)
class TargetContribution:
    """Loss contribution for one available target."""

    target_id: str
    metric: str
    observed: float
    target_value: float | None
    target_range: tuple[float, float] | None
    normalized_error: float
    weight: float
    weighted_error: float

    def to_mapping(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "metric": self.metric,
            "observed": self.observed,
            "target_value": self.target_value,
            "target_range": None if self.target_range is None else list(self.target_range),
            "normalized_error": self.normalized_error,
            "weight": self.weight,
            "weighted_error": self.weighted_error,
        }


@dataclass(frozen=True)
class CalibrationCandidate:
    """One evaluated point in the declared parameter grid."""

    parameters: dict[str, Any]
    metrics: dict[str, Any]
    status: str
    loss: float | None
    available_target_ids: tuple[str, ...]
    missing_target_ids: tuple[str, ...]
    contributions: tuple[TargetContribution, ...] = ()
    error: str | None = None

    def to_mapping(self) -> dict[str, Any]:
        return {
            "parameters": dict(self.parameters),
            "metrics": dict(self.metrics),
            "status": self.status,
            "loss": self.loss,
            "available_target_ids": list(self.available_target_ids),
            "missing_target_ids": list(self.missing_target_ids),
            "contributions": [item.to_mapping() for item in self.contributions],
            "error": self.error,
        }


@dataclass(frozen=True)
class CalibrationResult:
    """Complete deterministic calibration report."""

    status: str
    method: str
    target_count: int
    numeric_target_count: int
    candidate_count: int
    best_candidate: CalibrationCandidate | None
    candidates: tuple[CalibrationCandidate, ...]
    holdout: dict[str, Any]
    provenance: dict[str, Any]

    def to_mapping(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "method": self.method,
            "target_count": self.target_count,
            "numeric_target_count": self.numeric_target_count,
            "candidate_count": self.candidate_count,
            "best_candidate": (
                None if self.best_candidate is None else self.best_candidate.to_mapping()
            ),
            "candidates": [candidate.to_mapping() for candidate in self.candidates],
            "holdout": dict(self.holdout),
            "provenance": dict(self.provenance),
            "scientific_scope": (
                "Calibration is limited to matching supplied numeric literature "
                "observations. It does not establish disease validity or clinical meaning."
            ),
        }


def calibrate_grid(
    evaluator: MetricEvaluator,
    parameter_grid: Mapping[str, Sequence[float]],
    targets: Iterable[PhenotypeTarget],
    *,
    holdout_targets: Iterable[PhenotypeTarget] = (),
    random_seed: int = 0,
    provenance: Mapping[str, Any] | None = None,
) -> CalibrationResult:
    """Select the lowest-loss point from a deterministic parameter grid.

    The evaluator is supplied by the caller and may invoke the existing
    FlyGym experiment runner.  This function never runs a simulation itself.
    Candidates with missing target metrics are retained for audit but are not
    eligible to become the selected calibration point.
    """

    target_list = tuple(targets)
    numeric_targets = tuple(target for target in target_list if target.numeric)
    grid = _validate_parameter_grid(parameter_grid)
    combinations = tuple(
        dict(zip(grid.keys(), values))
        for values in itertools.product(*(grid[key] for key in grid))
    )
    base_provenance = {
        "method": "deterministic_grid_search",
        "random_seed": int(random_seed),
        "parameter_grid": {key: list(values) for key, values in grid.items()},
        "target_ids": [target.target_id for target in target_list],
        "numeric_target_ids": [target.target_id for target in numeric_targets],
        "created_at_utc": datetime.now(UTC).isoformat(),
    }
    if provenance:
        base_provenance["caller"] = dict(provenance)
    if not numeric_targets:
        return CalibrationResult(
            status="UNAVAILABLE_NUMERIC_TARGET",
            method="deterministic_grid_search",
            target_count=len(target_list),
            numeric_target_count=0,
            candidate_count=0,
            best_candidate=None,
            candidates=(),
            holdout={"status": "UNAVAILABLE_NUMERIC_TARGET"},
            provenance=base_provenance,
        )

    candidates: list[CalibrationCandidate] = []
    for parameters in combinations:
        try:
            raw_metrics = evaluator(parameters)
            metrics = dict(raw_metrics)
            candidate = _score_candidate(parameters, metrics, numeric_targets)
        except Exception as error:  # noqa: BLE001 - retain failed candidates for audit
            candidate = CalibrationCandidate(
                parameters=dict(parameters),
                metrics={},
                status="FAILED",
                loss=None,
                available_target_ids=(),
                missing_target_ids=tuple(target.target_id for target in numeric_targets),
                error=f"{type(error).__name__}: {error}",
            )
        candidates.append(candidate)

    eligible = [candidate for candidate in candidates if candidate.status == "PASS"]
    best = min(eligible, key=lambda candidate: candidate.loss) if eligible else None
    if best is None:
        status = "FAILED_NO_COMPLETE_CANDIDATE" if candidates else "FAILED"
    else:
        status = "PASS"

    holdout = {"status": "NOT_REQUESTED"}
    holdout_list = tuple(holdout_targets)
    if holdout_list:
        if best is None:
            holdout = {"status": "UNAVAILABLE_BEST_CANDIDATE"}
        else:
            holdout = evaluate_targets(evaluator(best.parameters), holdout_list)

    return CalibrationResult(
        status=status,
        method="deterministic_grid_search",
        target_count=len(target_list),
        numeric_target_count=len(numeric_targets),
        candidate_count=len(candidates),
        best_candidate=best,
        candidates=tuple(candidates),
        holdout=holdout,
        provenance=base_provenance,
    )


def evaluate_targets(
    metrics: Mapping[str, Any], targets: Iterable[PhenotypeTarget]
) -> dict[str, Any]:
    """Score a supplied metric mapping against targets without selecting params."""

    target_list = tuple(targets)
    numeric_targets = tuple(target for target in target_list if target.numeric)
    if not numeric_targets:
        return {"status": "UNAVAILABLE_NUMERIC_TARGET", "target_count": len(target_list)}
    candidate = _score_candidate({}, dict(metrics), numeric_targets)
    return {
        "status": candidate.status,
        "loss": candidate.loss,
        "available_target_ids": list(candidate.available_target_ids),
        "missing_target_ids": list(candidate.missing_target_ids),
        "contributions": [item.to_mapping() for item in candidate.contributions],
    }


def calibrate_candidates(
    candidates: Iterable[tuple[Mapping[str, Any], Mapping[str, Any]]],
    targets: Iterable[PhenotypeTarget],
    *,
    provenance: Mapping[str, Any] | None = None,
) -> CalibrationResult:
    """Select among already evaluated candidate reports.

    This is useful when simulations have already been run and archived. The
    candidate metric mappings are never regenerated or imputed.
    """

    target_list = tuple(targets)
    numeric_targets = tuple(target for target in target_list if target.numeric)
    base_provenance = {
        "method": "deterministic_candidate_evaluation",
        "target_ids": [target.target_id for target in target_list],
        "numeric_target_ids": [target.target_id for target in numeric_targets],
        "created_at_utc": datetime.now(UTC).isoformat(),
    }
    if provenance:
        base_provenance["caller"] = dict(provenance)
    if not numeric_targets:
        return CalibrationResult(
            status="UNAVAILABLE_NUMERIC_TARGET",
            method="deterministic_candidate_evaluation",
            target_count=len(target_list),
            numeric_target_count=0,
            candidate_count=0,
            best_candidate=None,
            candidates=(),
            holdout={"status": "UNAVAILABLE_NUMERIC_TARGET"},
            provenance=base_provenance,
        )

    scored = []
    for parameters, metrics in candidates:
        scored.append(
            _score_candidate(dict(parameters), dict(metrics), numeric_targets)
        )
    eligible = [candidate for candidate in scored if candidate.status == "PASS"]
    best = min(eligible, key=lambda candidate: candidate.loss) if eligible else None
    return CalibrationResult(
        status="PASS" if best is not None else "FAILED_NO_COMPLETE_CANDIDATE",
        method="deterministic_candidate_evaluation",
        target_count=len(target_list),
        numeric_target_count=len(numeric_targets),
        candidate_count=len(scored),
        best_candidate=best,
        candidates=tuple(scored),
        holdout={"status": "NOT_REQUESTED"},
        provenance=base_provenance,
    )


def write_calibration_report(result: CalibrationResult, path: str | Path) -> Path:
    """Write one JSON calibration report and return its path."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result.to_mapping(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination


def _score_candidate(
    parameters: Mapping[str, Any],
    metrics: dict[str, Any],
    targets: Sequence[PhenotypeTarget],
) -> CalibrationCandidate:
    available: list[str] = []
    missing: list[str] = []
    contributions: list[TargetContribution] = []
    for target in targets:
        observed = _finite_float(metrics.get(target.metric))
        if observed is None:
            missing.append(target.target_id)
            continue
        available.append(target.target_id)
        normalized_error = _normalized_error(observed, target)
        contributions.append(
            TargetContribution(
                target_id=target.target_id,
                metric=target.metric,
                observed=observed,
                target_value=target.target_value,
                target_range=target.target_range,
                normalized_error=normalized_error,
                weight=target.weight,
                weighted_error=normalized_error * target.weight,
            )
        )
    if not available:
        status = "UNAVAILABLE_METRICS"
        loss = None
    elif missing:
        status = "PARTIAL"
        loss = _weighted_loss(contributions)
    else:
        status = "PASS"
        loss = _weighted_loss(contributions)
    return CalibrationCandidate(
        parameters=_json_parameters(parameters),
        metrics=metrics,
        status=status,
        loss=loss,
        available_target_ids=tuple(available),
        missing_target_ids=tuple(missing),
        contributions=tuple(contributions),
    )


def _normalized_error(observed: float, target: PhenotypeTarget) -> float:
    if target.target_range is not None:
        lower, upper = target.target_range
        distance = 0.0 if lower <= observed <= upper else min(abs(observed - lower), abs(observed - upper))
        scale = target.scale or max(abs(upper - lower), 1.0)
        return distance / scale
    assert target.target_value is not None
    if target.direction == "lower":
        error = max(0.0, observed - target.target_value)
    elif target.direction == "higher":
        error = max(0.0, target.target_value - observed)
    else:
        error = abs(observed - target.target_value)
    scale = target.scale or max(abs(target.target_value), 1.0)
    return error / scale


def _weighted_loss(contributions: Sequence[TargetContribution]) -> float:
    total_weight = sum(item.weight for item in contributions)
    if total_weight <= 0:
        return math.inf
    return float(sum(item.weighted_error for item in contributions) / total_weight)


def _validate_parameter_grid(
    parameter_grid: Mapping[str, Sequence[float]],
) -> dict[str, tuple[float, ...]]:
    if not parameter_grid:
        raise CalibrationError("parameter_grid must contain at least one parameter.")
    result: dict[str, tuple[float, ...]] = {}
    for name, values in parameter_grid.items():
        if not str(name).strip():
            raise CalibrationError("parameter names must be non-empty.")
        converted = tuple(float(value) for value in values)
        if not converted or not all(math.isfinite(value) for value in converted):
            raise CalibrationError(f"parameter_grid[{name!r}] must contain finite values.")
        result[str(name)] = converted
    return result


def _finite_float(value: Any) -> float | None:
    try:
        converted = float(value)
    except (TypeError, ValueError):
        return None
    return converted if math.isfinite(converted) else None


def _json_parameters(parameters: Mapping[str, Any]) -> dict[str, Any]:
    """Preserve scalar and structured parameter provenance for reports."""

    result: dict[str, Any] = {}
    for key, value in parameters.items():
        if isinstance(value, (list, tuple)):
            result[str(key)] = list(value)
        elif isinstance(value, bool):
            result[str(key)] = value
        elif isinstance(value, (int, float)):
            numeric = float(value)
            if not math.isfinite(numeric):
                raise CalibrationError(f"Parameter {key!r} must be finite.")
            result[str(key)] = numeric
        elif value is None or isinstance(value, str):
            result[str(key)] = value
        else:
            raise CalibrationError(
                f"Parameter {key!r} is not JSON-compatible: {type(value).__name__}."
            )
    return result


__all__ = [
    "CalibrationCandidate",
    "CalibrationError",
    "CalibrationResult",
    "MetricEvaluator",
    "TargetContribution",
    "calibrate_grid",
    "calibrate_candidates",
    "evaluate_targets",
    "write_calibration_report",
]
