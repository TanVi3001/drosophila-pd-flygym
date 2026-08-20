"""Statistical validation helpers for calibration reports.

These functions operate on supplied values and callbacks only. They do not run
simulations or assert biological validity.
"""

from __future__ import annotations

from collections import defaultdict
import math
import random
from statistics import mean
from typing import Any, Callable, Iterable, Mapping, Sequence

from .calibration_engine import CalibrationRun


def rmse(observed: Sequence[float], expected: Sequence[float]) -> float | None:
    pairs = _finite_pairs(observed, expected)
    if not pairs:
        return None
    return math.sqrt(sum((a - b) ** 2 for a, b in pairs) / len(pairs))


def mae(observed: Sequence[float], expected: Sequence[float]) -> float | None:
    pairs = _finite_pairs(observed, expected)
    if not pairs:
        return None
    return sum(abs(a - b) for a, b in pairs) / len(pairs)


def r_squared(observed: Sequence[float], expected: Sequence[float]) -> float | None:
    pairs = _finite_pairs(observed, expected)
    if len(pairs) < 2:
        return None
    expected_mean = mean(item[1] for item in pairs)
    total = sum((item[1] - expected_mean) ** 2 for item in pairs)
    if total == 0:
        return None
    residual = sum((item[0] - item[1]) ** 2 for item in pairs)
    return 1.0 - residual / total


def pearson(observed: Sequence[float], expected: Sequence[float]) -> float | None:
    pairs = _finite_pairs(observed, expected)
    if len(pairs) < 2:
        return None
    left = [item[0] for item in pairs]
    right = [item[1] for item in pairs]
    left_mean = mean(left)
    right_mean = mean(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in pairs)
    denominator = math.sqrt(
        sum((a - left_mean) ** 2 for a in left)
        * sum((b - right_mean) ** 2 for b in right)
    )
    return None if denominator == 0 else numerator / denominator


def spearman(observed: Sequence[float], expected: Sequence[float]) -> float | None:
    pairs = _finite_pairs(observed, expected)
    if len(pairs) < 2:
        return None
    return pearson(_ranks([item[0] for item in pairs]), _ranks([item[1] for item in pairs]))


def bootstrap_ci(
    values: Sequence[float],
    statistic: Callable[[Sequence[float]], float] = lambda items: mean(items),
    *,
    repetitions: int = 1000,
    confidence: float = 0.95,
    random_seed: int = 0,
) -> dict[str, Any]:
    """Return a deterministic percentile bootstrap interval when possible."""

    clean = [float(value) for value in values if _finite(value)]
    if len(clean) < 2:
        return {"status": "UNAVAILABLE_INSUFFICIENT_VALUES", "count": len(clean)}
    if repetitions <= 0 or not 0 < confidence < 1:
        raise ValueError("repetitions must be positive and confidence must be in (0, 1).")
    rng = random.Random(random_seed)
    samples = [statistic([rng.choice(clean) for _ in clean]) for _ in range(repetitions)]
    alpha = (1.0 - confidence) / 2.0
    return {
        "status": "PASS",
        "count": len(clean),
        "repetitions": repetitions,
        "confidence": confidence,
        "estimate": statistic(clean),
        "lower": _percentile(samples, alpha),
        "upper": _percentile(samples, 1.0 - alpha),
        "random_seed": random_seed,
    }


def leave_one_group_out(
    records: Iterable[Mapping[str, Any]],
    group_key: str,
    evaluator: Callable[[tuple[Mapping[str, Any], ...]], Mapping[str, Any]],
) -> tuple[dict[str, Any], ...]:
    """Run a caller-supplied validation callback once per held-out group."""

    record_list = tuple(records)
    groups: dict[Any, list[Mapping[str, Any]]] = defaultdict(list)
    for record in record_list:
        groups[record.get(group_key)].append(record)
    results = []
    for held_out, group_records in sorted(groups.items(), key=lambda item: str(item[0])):
        training = tuple(record for record in record_list if record.get(group_key) != held_out)
        evaluation = dict(evaluator(training))
        results.append({"held_out": held_out, "training_count": len(training), **evaluation})
    return tuple(results)


def leave_one_paper_out(
    records: Iterable[Mapping[str, Any]],
    evaluator: Callable[[tuple[Mapping[str, Any], ...]], Mapping[str, Any]],
) -> tuple[dict[str, Any], ...]:
    return leave_one_group_out(records, "paper_id", evaluator)


def leave_one_condition_out(
    records: Iterable[Mapping[str, Any]],
    evaluator: Callable[[tuple[Mapping[str, Any], ...]], Mapping[str, Any]],
) -> tuple[dict[str, Any], ...]:
    return leave_one_group_out(records, "condition_id", evaluator)


def validate_calibration_run(run: CalibrationRun) -> dict[str, Any]:
    """Validate structural integrity of a calibration run without rerunning it."""

    errors: list[str] = []
    ids = [candidate.candidate_id for candidate in run.candidates]
    if len(ids) != len(set(ids)):
        errors.append("candidate_id values are not unique")
    if run.best_candidate_id is not None and run.best_candidate_id not in ids:
        errors.append("best_candidate_id is not present in candidates")
    for candidate in run.candidates:
        if candidate.objective.loss is not None and not _finite(candidate.objective.loss):
            errors.append(f"non-finite loss for {candidate.candidate_id}")
    return {
        "valid": not errors,
        "errors": errors,
        "candidate_count": run.candidate_count,
        "target_count": run.target_count,
        "numeric_target_count": run.numeric_target_count,
        "simulation_executed_by_engine": False,
    }


def _finite_pairs(left: Sequence[float], right: Sequence[float]) -> list[tuple[float, float]]:
    return [
        (float(a), float(b))
        for a, b in zip(left, right)
        if _finite(a) and _finite(b)
    ]


def _ranks(values: Sequence[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    result = [0.0] * len(values)
    cursor = 0
    while cursor < len(indexed):
        end = cursor + 1
        while end < len(indexed) and indexed[end][1] == indexed[cursor][1]:
            end += 1
        rank = (cursor + 1 + end) / 2.0
        for index in range(cursor, end):
            result[indexed[index][0]] = rank
        cursor = end
    return result


def _percentile(values: Sequence[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    weight = position - lower
    return float(ordered[lower] * (1 - weight) + ordered[upper] * weight)


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


__all__ = [
    "bootstrap_ci",
    "leave_one_condition_out",
    "leave_one_group_out",
    "leave_one_paper_out",
    "mae",
    "pearson",
    "r_squared",
    "rmse",
    "spearman",
    "validate_calibration_run",
]
