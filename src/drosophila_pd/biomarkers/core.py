"""Computational biomarker calculations over imported artifacts.

This module deliberately consumes only ``metrics.json`` and ``rollout.json``.
It never imports the simulation layer and never assigns a biological or
clinical interpretation to a score. Missing channels are represented by the
literal value ``"unavailable"``.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class DatasetArtifacts:
    """The source documents discovered for one dataset."""

    dataset_id: str
    dataset_dir: Path
    metrics: dict[str, Any]
    rollout: dict[str, Any]
    metrics_path: Path | None
    rollout_path: Path | None

    @property
    def frames(self) -> list[Mapping[str, Any]]:
        value = self.rollout.get("frames", [])
        return [item for item in value if isinstance(item, Mapping)] if isinstance(value, list) else []

    @property
    def source_files(self) -> tuple[str, ...]:
        return tuple(
            path.name
            for path in (self.metrics_path, self.rollout_path)
            if path is not None
        )


@dataclass(frozen=True)
class BiomarkerValue:
    """One biomarker value with its provenance and calculation description."""

    name: str
    value: float | str
    unit: str
    formula: str
    source: tuple[str, ...]
    details: dict[str, Any]

    @property
    def available(self) -> bool:
        return self.value != UNAVAILABLE

    def as_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "status": "available" if self.available else UNAVAILABLE,
            "unit": self.unit,
            "formula": self.formula,
            "source": list(self.source),
            "details": _json_value(self.details),
        }


@dataclass(frozen=True)
class BiomarkerReport:
    """Calculated biomarkers and the compact signals used by the dashboard."""

    dataset_id: str
    dataset_dir: Path
    biomarkers: dict[str, BiomarkerValue]
    source_files: tuple[str, ...]
    signals: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        available = sum(item.available for item in self.biomarkers.values())
        return {
            "schema_version": 1,
            "dataset_id": self.dataset_id,
            "scientific_scope": (
                "Computational summaries of imported rollout artifacts only; "
                "the composite score is not a Parkinson's disease diagnosis, "
                "biological severity estimate, or clinical measure."
            ),
            "source_files": list(self.source_files),
            "available_count": available,
            "unavailable_count": len(self.biomarkers) - available,
            "biomarkers": {name: value.as_dict() for name, value in self.biomarkers.items()},
            "signals": _json_value(self.signals),
        }


def load_artifacts(dataset: str | Path) -> DatasetArtifacts:
    """Load existing metrics and rollout JSON without invoking analysis."""

    requested = Path(dataset).expanduser()
    if requested.is_file() and requested.name == "metrics.json" and requested.parent.name == "metrics":
        root = requested.parent.parent
    else:
        root = requested.parent if requested.is_file() else requested
    root = root.resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Dataset directory not found: {dataset}")

    metrics_candidates = (root / "metrics" / "metrics.json", root / "metrics.json")
    rollout_path = root / "rollout.json"
    metrics_path = next((path for path in metrics_candidates if path.is_file()), None)
    rollout_file = rollout_path if rollout_path.is_file() else None
    if metrics_path is None and rollout_file is None:
        raise FileNotFoundError(f"No metrics.json or rollout.json found under {root}")

    metrics = _read_object(metrics_path) if metrics_path else {}
    rollout = _read_object(rollout_file) if rollout_file else {}
    nested_rollout = rollout.get("rollout")
    if isinstance(nested_rollout, Mapping):
        rollout = dict(nested_rollout)
    metadata = metrics.get("metadata") if isinstance(metrics.get("metadata"), Mapping) else {}
    dataset_id = metrics.get("dataset_id") or metadata.get("dataset_id") or root.name
    return DatasetArtifacts(
        dataset_id=str(dataset_id),
        dataset_dir=root,
        metrics=metrics,
        rollout=rollout,
        metrics_path=metrics_path,
        rollout_path=rollout_file,
    )


def calculate_biomarkers(dataset: str | Path | DatasetArtifacts) -> BiomarkerReport:
    """Calculate bounded computational summaries from imported JSON artifacts."""

    artifacts = dataset if isinstance(dataset, DatasetArtifacts) else load_artifacts(dataset)
    metrics = artifacts.metrics
    trajectory = _trajectory(artifacts)
    time_s = _time_series(artifacts, trajectory.shape[0] if trajectory is not None else None)
    heading = _heading_series(artifacts, time_s)
    curvature = _curvature_series(metrics)
    contacts, contact_times = _contact_series(artifacts, time_s)
    pause = _pause_series(artifacts.frames)

    locomotion_efficiency = _locomotion_efficiency(metrics, trajectory)
    turning_stability = _turning_stability(curvature, heading, time_s)
    orientation_drift = _orientation_drift(heading)
    stride_variability = _stride_variability(contacts, contact_times)
    symmetry = _symmetry_score(metrics, contacts)
    pause_ratio = _pause_ratio(pause)
    trajectory_complexity = _trajectory_complexity(locomotion_efficiency)

    stride_stability = (
        1.0 / (1.0 + float(stride_variability.value))
        if _available("stride_variability", stride_variability)
        else None
    )
    gait_components = {
        "symmetry_score": symmetry.value if symmetry.available else None,
        "stride_stability_score": stride_stability,
        "turning_stability": turning_stability.value if turning_stability.available else None,
    }
    gait_stability = _composite(
        "gait_stability_index",
        gait_components,
        "mean(symmetry_score, 1/(1+stride_variability), turning_stability)",
        "0-1 index; higher values indicate greater computational stability under this definition",
    )

    motor_components = {
        "path_inefficiency": _inverse_unit_score(locomotion_efficiency),
        "pause_ratio": pause_ratio.value if pause_ratio.available else None,
        "orientation_drift_score": _bounded_angle_score(orientation_drift),
    }
    motor_impairment = _composite(
        "motor_impairment_index",
        motor_components,
        "mean(1-locomotion_efficiency, pause_ratio, min(abs(orientation_drift)/pi, 1))",
        "0-1 computational composite; higher values indicate more impairment components under this definition",
    )

    coordination_components = {
        "symmetry_inequality": 1.0 - float(symmetry.value) if symmetry.available else None,
        "stride_variability_score": (
            float(stride_variability.value) / (1.0 + float(stride_variability.value))
            if stride_variability.available
            else None
        ),
        "turning_instability": (
            1.0 - float(turning_stability.value) if turning_stability.available else None
        ),
    }
    coordination_impairment = _composite(
        "coordination_impairment_index",
        coordination_components,
        "mean(1-symmetry_score, stride_variability/(1+stride_variability), 1-turning_stability)",
        "0-1 computational composite; not a biological coordination diagnosis",
    )

    severity = _composite(
        "disease_severity_score",
        {
            "motor_impairment_index": motor_impairment.value if motor_impairment.available else None,
            "coordination_impairment_index": coordination_impairment.value if coordination_impairment.available else None,
            "trajectory_complexity": trajectory_complexity.value if trajectory_complexity.available else None,
        },
        "mean(available computational impairment components)",
        "0-1 computational composite only; it is not a Parkinson's disease score",
    )

    values = {
        "gait_stability_index": gait_stability,
        "locomotion_efficiency": locomotion_efficiency,
        "turning_stability": turning_stability,
        "orientation_drift": orientation_drift,
        "stride_variability": stride_variability,
        "symmetry_score": symmetry,
        "motor_impairment_index": motor_impairment,
        "coordination_impairment_index": coordination_impairment,
        "trajectory_complexity": trajectory_complexity,
        "pause_ratio": pause_ratio,
        "disease_severity_score": severity,
    }
    signals: dict[str, Any] = {}
    if time_s is not None:
        signals["time_s"] = time_s
    if trajectory is not None:
        signals["trajectory_xy"] = trajectory[:, :2]
    if heading is not None:
        signals["heading_angle_rad"] = heading
    return BiomarkerReport(
        dataset_id=artifacts.dataset_id,
        dataset_dir=artifacts.dataset_dir,
        biomarkers=values,
        source_files=artifacts.source_files,
        signals=signals,
    )


def _read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, Mapping):
        raise ValueError(f"JSON document must contain an object: {path}")
    return dict(value)


def _metric(metrics: Mapping[str, Any], key: str) -> Any:
    scalar = metrics.get("scalar_metrics")
    if isinstance(scalar, Mapping) and key in scalar:
        return scalar[key]
    return metrics.get(key)


def _series_from_mapping(mapping: Mapping[str, Any], keys: Sequence[str]) -> np.ndarray | None:
    value: Any = None
    for key in keys:
        if key in mapping:
            value = mapping[key]
            break
    if value is None:
        return None
    try:
        array = np.asarray(value, dtype=float).reshape(-1)
    except (TypeError, ValueError):
        return None
    return array if array.size and np.isfinite(array).all() else None


def _trajectory(artifacts: DatasetArtifacts) -> np.ndarray | None:
    timeseries = artifacts.metrics.get("timeseries")
    if isinstance(timeseries, Mapping):
        for key in ("thorax_position", "thorax_positions", "trajectory"):
            if key in timeseries:
                array = _matrix(timeseries[key], 3)
                if array is not None:
                    return array
    for key in ("thorax_positions", "thorax", "positions", "trajectory"):
        if key in artifacts.metrics:
            array = _matrix(artifacts.metrics[key], 3)
            if array is not None:
                return array
    frames = artifacts.frames
    if not frames:
        return None
    values = [next((frame[key] for key in ("thorax", "thorax_position", "position") if key in frame), None) for frame in frames]
    return _matrix(values, 3) if all(value is not None for value in values) else None


def _time_series(artifacts: DatasetArtifacts, count: int | None) -> np.ndarray | None:
    timeseries = artifacts.metrics.get("timeseries")
    if isinstance(timeseries, Mapping):
        value = _series_from_mapping(timeseries, ("time_s", "timestamp_s", "timestamps_s"))
        if value is not None and (count is None or value.size == count):
            return value
    frames = artifacts.frames
    if frames:
        values = [next((frame[key] for key in ("timestamp_s", "time", "timestamp") if key in frame), None) for frame in frames]
        if all(value is not None for value in values):
            array = _series_from_mapping({"time": values}, ("time",))
            if array is not None and (count is None or array.size == count):
                return array
        step = _positive(_metric(artifacts.metrics, "timestep_s"))
        if step is not None and (count is None or len(frames) == count):
            return np.arange(len(frames), dtype=float) * step
    return None


def _heading_series(artifacts: DatasetArtifacts, time_s: np.ndarray | None) -> np.ndarray | None:
    metrics = artifacts.metrics
    timeseries = metrics.get("timeseries")
    if isinstance(timeseries, Mapping):
        value = _series_from_mapping(timeseries, ("heading_angle_rad", "heading"))
        if value is not None:
            return value
    value = _series_from_mapping(metrics, ("heading_angle_rad", "heading"))
    if value is not None:
        return value
    orientation = _orientation_from_frames(artifacts.frames, metrics)
    if orientation is None:
        return None
    w, x, y, z = orientation.T
    return np.unwrap(np.arctan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z)))


def _orientation_from_frames(frames: Sequence[Mapping[str, Any]], metrics: Mapping[str, Any]) -> np.ndarray | None:
    if not frames:
        return None
    order = str(metrics.get("quaternion_order", "wxyz")).lower()
    values: list[list[float]] = []
    for frame in frames:
        raw = frame.get("orientation")
        if isinstance(raw, Mapping) and all(key in raw for key in ("qx", "qy", "qz", "qw")):
            values.append([float(raw["qw"]), float(raw["qx"]), float(raw["qy"]), float(raw["qz"])])
        elif raw is not None:
            try:
                values.append([float(value) for value in raw])
            except (TypeError, ValueError):
                return None
        else:
            return None
    array = _matrix(values, 4)
    if array is None:
        return None
    if order == "xyzw":
        array = array[:, [3, 0, 1, 2]]
    if order not in {"wxyz", "xyzw"}:
        return None
    norms = np.linalg.norm(array, axis=1)
    return array / norms[:, None] if np.all(norms > 0) else None


def _curvature_series(metrics: Mapping[str, Any]) -> np.ndarray | None:
    timeseries = metrics.get("timeseries")
    value = _series_from_mapping(timeseries, ("trajectory_curvature_rad_per_mm", "trajectory_curvature")) if isinstance(timeseries, Mapping) else None
    if value is not None:
        return value
    value = metrics.get("trajectory_curvature")
    if value is None:
        value = _metric(metrics, "trajectory_curvature_mean_rad_per_mm")
    if isinstance(value, (int, float)) and np.isfinite(float(value)):
        return np.asarray([float(value)])
    if value is not None:
        return _series_from_mapping({"value": value}, ("value",))
    return None


def _contact_series(artifacts: DatasetArtifacts, time_s: np.ndarray | None) -> tuple[dict[str, np.ndarray], np.ndarray | None]:
    frames = artifacts.frames
    if not frames:
        return {}, time_s
    values: list[Mapping[str, Any]] = []
    for frame in frames:
        raw = frame.get("contact", frame.get("contacts", frame.get("adhesion")))
        values.append(raw if isinstance(raw, Mapping) else {})
    labels = sorted({str(label) for item in values for label in item})
    if not labels:
        return {}, time_s
    result: dict[str, np.ndarray] = {}
    for label in labels:
        samples = []
        for item in values:
            raw = item.get(label)
            if raw is None:
                samples.append(0.0)
            else:
                array = np.asarray(raw, dtype=float)
                samples.append(float(np.any(array > 0.5)))
        result[label] = np.asarray(samples, dtype=float)
    return result, time_s


def _pause_series(frames: Sequence[Mapping[str, Any]]) -> np.ndarray | None:
    if not frames:
        return None
    result: list[float] = []
    found = False
    for frame in frames:
        value = next((frame[key] for key in ("pause", "paused", "is_pause", "is_paused") if key in frame), None)
        if value is None:
            state = next((frame[key] for key in ("behavior", "state", "label") if key in frame), None)
            value = str(state).strip().lower() in {"pause", "paused"} if state is not None else None
        if value is None:
            result.append(0.0)
        else:
            found = True
            result.append(float(bool(value)))
    return np.asarray(result, dtype=float) if found else None


def _locomotion_efficiency(metrics: Mapping[str, Any], trajectory: np.ndarray | None) -> BiomarkerValue:
    source = ("metrics.json", "rollout.json") if trajectory is not None else ("metrics.json",)
    if trajectory is None or trajectory.shape[0] < 2:
        return _unavailable("locomotion_efficiency", "displacement / path_length", "0-1", source, "trajectory has fewer than two samples")
    path_length = _positive(_metric(metrics, "total_distance_mm"))
    if path_length is None:
        path_length = float(np.linalg.norm(np.diff(trajectory[:, :2], axis=0), axis=1).sum())
    displacement = float(np.linalg.norm(trajectory[-1, :2] - trajectory[0, :2]))
    if path_length <= 0:
        return _unavailable("locomotion_efficiency", "displacement / path_length", "0-1", source, "path length is zero")
    return _value("locomotion_efficiency", min(displacement / path_length, 1.0), "0-1", "displacement / path_length", source, {"displacement_mm": displacement, "path_length_mm": path_length})


def _turning_stability(curvature: np.ndarray | None, heading: np.ndarray | None, time_s: np.ndarray | None) -> BiomarkerValue:
    source = ("metrics.json",)
    series = curvature
    if series is None and heading is not None and heading.size > 2:
        series = np.abs(np.diff(heading))
        source = ("metrics.json", "rollout.json")
    if series is None:
        return _unavailable("turning_stability", "1 / (1 + CV(abs(turning series)))", "0-1", source, "turning series unavailable")
    active = np.abs(np.asarray(series, dtype=float))
    active = active[np.isfinite(active) & (active > 1e-12)]
    if active.size < 2 or float(np.mean(active)) <= 0:
        return _unavailable("turning_stability", "1 / (1 + CV(abs(turning series)))", "0-1", source, "fewer than two non-zero turning samples")
    cv = float(np.std(active) / np.mean(active))
    return _value("turning_stability", 1.0 / (1.0 + cv), "0-1", "1 / (1 + CV(abs(turning series)))", source, {"turning_cv": cv})


def _orientation_drift(heading: np.ndarray | None) -> BiomarkerValue:
    if heading is None or heading.size < 2:
        return _unavailable("orientation_drift", "abs(heading_last - heading_first)", "rad", ("metrics.json", "rollout.json"), "heading series unavailable")
    value = float(abs(heading[-1] - heading[0]))
    return _value("orientation_drift", value, "rad", "abs(heading_last - heading_first)", ("metrics.json", "rollout.json"), {})


def _stride_variability(contacts: Mapping[str, np.ndarray], time_s: np.ndarray | None) -> BiomarkerValue:
    if not contacts or time_s is None:
        return _unavailable("stride_variability", "std(stride_intervals) / mean(stride_intervals)", "CV", ("rollout.json",), "contact timeline or timestamps unavailable")
    intervals: list[float] = []
    for values in contacts.values():
        active = np.asarray(values, dtype=float) > 0.5
        events = np.flatnonzero(active & ~np.concatenate(([False], active[:-1])))
        if events.size >= 3:
            intervals.extend(np.diff(time_s[events]).tolist())
    intervals_array = np.asarray(intervals, dtype=float)
    if intervals_array.size < 2 or float(np.mean(intervals_array)) <= 0:
        return _unavailable("stride_variability", "std(stride_intervals) / mean(stride_intervals)", "CV", ("rollout.json",), "fewer than two stride intervals")
    value = float(np.std(intervals_array) / np.mean(intervals_array))
    return _value("stride_variability", value, "CV", "std(stride_intervals) / mean(stride_intervals)", ("rollout.json",), {"interval_count": int(intervals_array.size)})


def _symmetry_score(metrics: Mapping[str, Any], contacts: Mapping[str, np.ndarray]) -> BiomarkerValue:
    raw = _metric(metrics, "symmetry_index")
    if isinstance(raw, (int, float)) and np.isfinite(float(raw)):
        return _value("symmetry_score", float(np.clip(raw, 0.0, 1.0)), "0-1", "existing symmetry_index", ("metrics.json",), {})
    ratios = _metric(metrics, "contact_ratio")
    if not isinstance(ratios, Mapping) and contacts:
        ratios = {name: float(np.mean(values > 0.5)) for name, values in contacts.items()}
    pairs = _paired_ratios(ratios if isinstance(ratios, Mapping) else {})
    if not pairs:
        return _unavailable("symmetry_score", "mean(1 - abs(L-R)/(L+R))", "0-1", ("metrics.json", "rollout.json"), "left/right pair data unavailable")
    scores = [1.0 - abs(left - right) / (left + right) if left + right else 1.0 for left, right in pairs.values()]
    return _value("symmetry_score", float(np.mean(scores)), "0-1", "mean(1 - abs(L-R)/(L+R))", ("metrics.json", "rollout.json"), {"pair_count": len(scores)})


def _pause_ratio(pause: np.ndarray | None) -> BiomarkerValue:
    if pause is None or pause.size == 0:
        return _unavailable("pause_ratio", "paused_frames / total_frames", "0-1", ("rollout.json",), "explicit pause/state channel unavailable")
    return _value("pause_ratio", float(np.mean(pause > 0.5)), "0-1", "paused_frames / total_frames", ("rollout.json",), {})


def _trajectory_complexity(efficiency: BiomarkerValue) -> BiomarkerValue:
    if not efficiency.available:
        return _unavailable("trajectory_complexity", "1 - locomotion_efficiency", "0-1", efficiency.source, "locomotion efficiency unavailable")
    return _value("trajectory_complexity", 1.0 - float(efficiency.value), "0-1", "1 - locomotion_efficiency", efficiency.source, {})


def _composite(name: str, components: Mapping[str, Any], formula: str, description: str) -> BiomarkerValue:
    values = [float(value) for value in components.values() if isinstance(value, (int, float)) and np.isfinite(float(value))]
    if not values:
        return _unavailable(name, formula, "0-1", ("metrics.json", "rollout.json"), "no usable component biomarker")
    return _value(name, float(np.clip(np.mean(values), 0.0, 1.0)), "0-1", formula, ("metrics.json", "rollout.json"), {"components": _json_value(components), "description": description})


def _available(name: str, item: BiomarkerValue) -> bool:
    return item.available and isinstance(item.value, (int, float)) and np.isfinite(float(item.value))


def _inverse_unit_score(value: BiomarkerValue) -> float | None:
    return 1.0 - float(value.value) if value.available else None


def _bounded_angle_score(value: BiomarkerValue) -> float | None:
    return min(float(value.value) / np.pi, 1.0) if value.available else None


def _paired_ratios(values: Mapping[str, Any]) -> dict[str, tuple[float, float]]:
    grouped: dict[str, dict[str, float]] = {}
    for name, raw in values.items():
        if not isinstance(raw, (int, float)) or not np.isfinite(float(raw)):
            continue
        text = "".join(character for character in str(name).upper() if character.isalnum())
        side = text[0] if text.startswith(("L", "R")) else None
        if side:
            grouped.setdefault(text[1:], {})[side] = float(raw)
    return {key: (item["L"], item["R"]) for key, item in grouped.items() if "L" in item and "R" in item}


def _matrix(value: Any, width: int) -> np.ndarray | None:
    try:
        array = np.asarray(value, dtype=float)
    except (TypeError, ValueError):
        return None
    if array.ndim != 2 or array.shape[1] != width or not array.shape[0] or not np.isfinite(array).all():
        return None
    return array


def _positive(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if np.isfinite(result) and result > 0 else None


def _value(name: str, value: float, unit: str, formula: str, source: tuple[str, ...], details: dict[str, Any]) -> BiomarkerValue:
    return BiomarkerValue(name, float(value), unit, formula, source, details)


def _unavailable(name: str, formula: str, unit: str, source: tuple[str, ...], reason: str) -> BiomarkerValue:
    return BiomarkerValue(name, UNAVAILABLE, unit, formula, source, {"reason": reason})


def _json_value(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return [_json_value(item) for item in value.tolist()]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


__all__ = [
    "UNAVAILABLE",
    "BiomarkerReport",
    "BiomarkerValue",
    "DatasetArtifacts",
    "calculate_biomarkers",
    "load_artifacts",
]
