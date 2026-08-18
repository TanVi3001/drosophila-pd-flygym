"""Post-process imported FlyGym rollout artifacts.

This module only reads rollout files. It does not run FlyGym, mutate a
simulation, or make biological claims. Missing optional channels are reported
as unavailable rather than inferred from unrelated data.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


@dataclass(frozen=True)
class LoadedRollout:
    """Normalized arrays used by the analysis layer."""

    dataset_id: str
    dataset_dir: Path
    metadata: dict[str, Any]
    time_s: np.ndarray
    thorax_positions: np.ndarray
    orientations_wxyz: np.ndarray | None
    com_positions: np.ndarray | None
    joint_positions: dict[str, np.ndarray]
    joint_velocity: dict[str, np.ndarray]
    joint_acceleration: dict[str, np.ndarray]
    contacts: dict[str, np.ndarray]
    source_files: tuple[Path, ...]
    quaternion_order: str | None
    timestamps_reconstructed: bool

    @property
    def frame_count(self) -> int:
        return int(self.thorax_positions.shape[0])

    @property
    def timestep_s(self) -> float:
        if self.time_s.size < 2:
            value = self.metadata.get("timestep_s", self.metadata.get("timestep", 1.0))
            return _positive_float(value, default=1.0)
        return float(np.median(np.diff(self.time_s)))


@dataclass(frozen=True)
class AnalysisResult:
    """In-memory metrics plus paths written by :func:`analyze_rollout`."""

    metrics: dict[str, Any]
    output_dir: Path
    files: dict[str, Path]


def load_rollout(dataset: str | Path) -> LoadedRollout:
    """Load ``rollout.json`` or ``rollout.npz`` from a dataset directory."""

    requested = Path(dataset).expanduser()
    if requested.is_file():
        root = requested.parent.resolve()
        json_path = requested if requested.suffix.lower() == ".json" else _first_file(root, ("rollout.json",))
        npz_path = requested if requested.suffix.lower() == ".npz" else _optional_file(root, ("rollout.npz", "rollout_arrays.npz"))
    else:
        root = requested.resolve()
        if not root.is_dir():
            raise FileNotFoundError(f"Dataset directory not found: {dataset}")
        json_path = _optional_file(root, ("rollout.json",))
        npz_path = _optional_file(root, ("rollout.npz", "rollout_arrays.npz"))
    if json_path is None and npz_path is None:
        raise FileNotFoundError(f"No rollout.json or rollout.npz found under {root}")

    payload: dict[str, Any] = {}
    frames: list[Any] = []
    if json_path is not None:
        raw = json.loads(json_path.read_text(encoding="utf-8"))
        if not isinstance(raw, Mapping):
            raise ValueError("rollout.json must contain an object")
        candidate = raw.get("rollout")
        payload = dict(candidate) if isinstance(candidate, Mapping) else dict(raw)
        raw_frames = payload.get("frames")
        if isinstance(raw_frames, Sequence) and not isinstance(raw_frames, (str, bytes)):
            frames = list(raw_frames)

    metadata = _read_metadata(root, payload)
    arrays = _read_npz(npz_path) if npz_path is not None else {}
    frame_count_hint = _frame_count_hint(payload, arrays, frames)
    positions = _required_positions(payload, arrays, frames, frame_count_hint)
    count = int(positions.shape[0])
    time_s, timestamps_reconstructed = _resolve_time(payload, arrays, frames, metadata, count)
    quaternions, quaternion_order = _optional_quaternions(payload, arrays, frames, metadata, count)
    com = _optional_matrix(payload, arrays, frames, count, 3, ("com_positions", "com", "COM"), ("com", "COM"))
    names = _joint_names(payload, metadata)
    joint_positions = _joint_series(payload, arrays, frames, count, names, "position")
    joint_velocity = _joint_series(payload, arrays, frames, count, names, "velocity")
    joint_acceleration = _joint_series(payload, arrays, frames, count, names, "acceleration")
    if not joint_velocity and joint_positions:
        joint_velocity = _differentiate(joint_positions, time_s)
    if not joint_acceleration and joint_velocity:
        joint_acceleration = _differentiate(joint_velocity, time_s)
    contacts = _contact_series(payload, arrays, frames, count)
    metadata.setdefault("dataset_id", root.name)
    metadata.setdefault("frame_count", count)
    metadata.setdefault("timestep_s", float(np.median(np.diff(time_s))) if count > 1 else 1.0)
    sources = tuple(path for path in (json_path, npz_path) if path is not None)
    return LoadedRollout(
        dataset_id=str(metadata["dataset_id"]),
        dataset_dir=root,
        metadata=metadata,
        time_s=time_s,
        thorax_positions=positions,
        orientations_wxyz=quaternions,
        com_positions=com,
        joint_positions=joint_positions,
        joint_velocity=joint_velocity,
        joint_acceleration=joint_acceleration,
        contacts=contacts,
        source_files=sources,
        quaternion_order=quaternion_order,
        timestamps_reconstructed=timestamps_reconstructed,
    )


def compute_metrics(rollout: LoadedRollout) -> dict[str, Any]:
    """Compute analysis metrics from a normalized imported rollout."""

    positions = rollout.thorax_positions
    time_s = rollout.time_s
    intervals = _intervals(time_s, rollout.timestep_s)
    planar_steps = np.diff(positions[:, :2], axis=0)
    step_distance = np.linalg.norm(planar_steps, axis=1) if positions.shape[0] > 1 else np.array([], dtype=float)
    step_speed = step_distance / intervals if step_distance.size else np.array([], dtype=float)
    instantaneous_speed = np.concatenate(([0.0], step_speed))
    total_distance = float(step_distance.sum())

    heading = _heading_series(rollout.orientations_wxyz)
    orientation = _orientation_series(rollout.orientations_wxyz)
    curvature = _curvature_series(heading, step_distance)
    com_velocity = _velocity_series(rollout.com_positions, time_s)
    contact = _contact_metrics(rollout.contacts, time_s, rollout.timestep_s)
    joint_velocity_rms = _rms_by_joint(rollout.joint_velocity)
    joint_acceleration_rms = _rms_by_joint(rollout.joint_acceleration)
    symmetry, symmetry_by_pair = _symmetry_metrics(rollout.contacts, joint_velocity_rms)

    scalar_metrics: dict[str, Any] = {
        "walking_speed_mm_s": _finite_or_none(np.mean(instantaneous_speed)),
        "walking_speed_max_mm_s": _finite_or_none(np.max(instantaneous_speed)),
        "total_distance_mm": total_distance,
        "com_velocity_mean_mm_s": _finite_or_none(np.mean(com_velocity)) if com_velocity is not None else None,
        "heading_variance_rad2": _finite_or_none(np.var(heading)) if heading is not None else None,
        "stride_frequency_hz": contact["stride_frequency_hz"],
        "step_frequency_hz": contact["step_frequency_hz"],
        "body_orientation_variance_rad2": orientation["variance_rad2"] if orientation else None,
        "symmetry_index": symmetry,
        "trajectory_curvature_mean_rad_per_mm": (
            _finite_or_none(np.mean(np.abs(curvature))) if curvature.size else None
        ),
    }
    return {
        "analysis_version": 1,
        "scientific_scope": (
            "Computational metrics calculated from imported rollout files only; "
            "not biological validation or a clinical Parkinson's disease measure."
        ),
        "dataset_id": rollout.dataset_id,
        "source_files": [path.name for path in rollout.source_files],
        "frame_count": rollout.frame_count,
        "duration_s": float(time_s[-1] - time_s[0]) if time_s.size > 1 else 0.0,
        "timestep_s": rollout.timestep_s,
        "timestamps_reconstructed": rollout.timestamps_reconstructed,
        "quaternion_order": rollout.quaternion_order,
        "scalar_metrics": scalar_metrics,
        **scalar_metrics,
        "com_trajectory": _json_value(rollout.com_positions),
        "com_velocity_mm_s": _json_value(com_velocity),
        "heading_angle_rad": _json_value(heading),
        "body_orientation_variance": orientation,
        "joint_rms_velocity": joint_velocity_rms,
        "joint_rms_acceleration": joint_acceleration_rms,
        "contact_ratio": contact["ratio"],
        "contact_duration_s": contact["duration_s"],
        "contact_available": contact["available"],
        "symmetry_index_by_pair": symmetry_by_pair,
        "trajectory_curvature": _json_value(curvature),
        "timeseries": {
            "time_s": _json_value(time_s),
            "thorax_position": _json_value(positions),
            "instantaneous_speed_mm_s": _json_value(instantaneous_speed),
            "step_distance_mm": _json_value(step_distance),
            "heading_angle_rad": _json_value(heading),
            "trajectory_curvature_rad_per_mm": _json_value(curvature),
            "com_velocity_mm_s": _json_value(com_velocity),
        },
        "available_channels": {
            "orientation": rollout.orientations_wxyz is not None,
            "com": rollout.com_positions is not None,
            "joint_velocity": bool(rollout.joint_velocity),
            "joint_acceleration": bool(rollout.joint_acceleration),
            "contacts": bool(rollout.contacts),
        },
    }


def analyze_rollout(dataset: str | Path, output_dir: str | Path = "results") -> AnalysisResult:
    """Load a rollout, compute metrics, and write the analysis package."""

    rollout = load_rollout(dataset)
    metrics = compute_metrics(rollout)
    from .report import write_analysis_report

    return write_analysis_report(metrics, rollout, output_dir)


def _read_npz(path: Path | None) -> dict[str, np.ndarray]:
    if path is None:
        return {}
    with np.load(path, allow_pickle=False) as archive:
        return {key: np.asarray(archive[key]) for key in archive.files}


def _read_metadata(root: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(payload.get("metadata", {})) if isinstance(payload.get("metadata"), Mapping) else {}
    metadata_path = root / "metadata.json"
    if metadata_path.is_file():
        raw = json.loads(metadata_path.read_text(encoding="utf-8"))
        if isinstance(raw, Mapping):
            result = {**dict(raw), **result}
    return result


def _required_positions(payload: Mapping[str, Any], arrays: Mapping[str, np.ndarray], frames: Sequence[Any], count_hint: int) -> np.ndarray:
    value = _first_array(arrays, ("thorax_positions", "thorax", "positions"))
    if value is None:
        value = _first_value(payload, ("thorax_positions", "thorax", "positions"))
    if value is None and frames:
        value = [item.get("thorax", item.get("position")) if isinstance(item, Mapping) else None for item in frames]
    matrix = _as_matrix(value, 3, "thorax_positions", count_hint or None)
    if matrix is None:
        raise ValueError("rollout requires thorax positions")
    return matrix


def _optional_quaternions(
    payload: Mapping[str, Any],
    arrays: Mapping[str, np.ndarray],
    frames: Sequence[Any],
    metadata: Mapping[str, Any],
    count: int,
) -> tuple[np.ndarray | None, str | None]:
    order = str(metadata.get("quaternion_order", "wxyz")).lower()
    value = None
    for key in ("thorax_quaternions_xyzw", "quaternions_xyzw"):
        if key in arrays:
            value, order = arrays[key], "xyzw"
            break
    if value is None:
        for key in ("thorax_quaternions", "quaternions", "orientation"):
            if key in arrays:
                value = arrays[key]
                break
    if value is None:
        value = _first_value(payload, ("thorax_quaternions_xyzw", "quaternions_xyzw"))
        if value is not None:
            order = "xyzw"
    if value is None:
        value = _first_value(payload, ("thorax_quaternions", "quaternions", "orientation"))
    if value is None and frames:
        values: list[Any] = []
        frame_order = order
        for item in frames:
            orientation = item.get("orientation") if isinstance(item, Mapping) else None
            if isinstance(orientation, Mapping) and all(key in orientation for key in ("qx", "qy", "qz", "qw")):
                values.append([orientation["qx"], orientation["qy"], orientation["qz"], orientation["qw"]])
                frame_order = "xyzw"
            else:
                values.append(orientation)
        if any(item is not None for item in values):
            value, order = values, frame_order
    matrix = _as_matrix(value, 4, "orientation", count)
    if matrix is None:
        return None, None
    if order not in {"wxyz", "xyzw"}:
        raise ValueError("quaternion_order must be 'wxyz' or 'xyzw'")
    if order == "xyzw":
        matrix = matrix[:, [3, 0, 1, 2]]
    norms = np.linalg.norm(matrix, axis=1)
    if not np.isfinite(matrix).all() or np.any(norms <= 0) or not np.isfinite(norms).all():
        raise ValueError("orientation contains non-finite or zero-norm quaternions")
    return matrix / norms[:, None], order


def _optional_matrix(
    payload: Mapping[str, Any],
    arrays: Mapping[str, np.ndarray],
    frames: Sequence[Any],
    count: int,
    width: int,
    array_keys: Sequence[str],
    frame_keys: Sequence[str],
) -> np.ndarray | None:
    value = _first_array(arrays, array_keys)
    if value is None:
        value = _first_value(payload, array_keys)
    if value is None and frames:
        values = [next((item.get(key) for key in frame_keys if isinstance(item, Mapping) and key in item), None) for item in frames]
        if any(item is not None for item in values):
            value = values
    return _as_matrix(value, width, array_keys[0], count)


def _joint_names(payload: Mapping[str, Any], metadata: Mapping[str, Any]) -> list[str]:
    for value in (payload.get("joint_names"), metadata.get("joint_names")):
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            return [str(item) for item in value]
    return []


def _joint_series(
    payload: Mapping[str, Any],
    arrays: Mapping[str, np.ndarray],
    frames: Sequence[Any],
    count: int,
    names: Sequence[str],
    kind: str,
) -> dict[str, np.ndarray]:
    prefixes = {
        "position": ("joint__",),
        "velocity": ("joint_velocity__", "joint_velocities__"),
        "acceleration": ("joint_acceleration__", "joint_accelerations__"),
    }[kind]
    result = {
        key[len(prefix):]: _series(value, count, key)
        for key, value in arrays.items()
        for prefix in prefixes
        if key.startswith(prefix)
    }
    matrix_keys = {
        "position": ("joint_positions", "joint_angles"),
        "velocity": ("joint_velocity", "joint_velocities"),
        "acceleration": ("joint_acceleration", "joint_accelerations"),
    }[kind]
    if not result:
        matrix = _first_array(arrays, matrix_keys)
        if matrix is None:
            matrix = _first_value(payload, matrix_keys)
        if matrix is not None:
            if isinstance(matrix, Mapping):
                result = {
                    str(name): _series(value, count, f"{kind}[{name}]")
                    for name, value in matrix.items()
                }
            else:
                result = _matrix_to_series(matrix, names, count, kind)
    if not result and frames:
        keys = matrix_keys
        values = [next((item.get(key) for key in keys if isinstance(item, Mapping) and key in item), None) for item in frames]
        if any(item is not None for item in values):
            if all(isinstance(item, Mapping) for item in values):
                labels = sorted({str(label) for item in values for label in item})
                result = {label: _series([item.get(label) for item in values], count, label) for label in labels}
            else:
                result = _matrix_to_series(values, names, count, kind)
    return result


def _contact_series(payload: Mapping[str, Any], arrays: Mapping[str, np.ndarray], frames: Sequence[Any], count: int) -> dict[str, np.ndarray]:
    result: dict[str, np.ndarray] = {}
    for key, value in arrays.items():
        prefix = next((item for item in ("contact__", "adhesion__") if key.startswith(item)), None)
        if prefix:
            array = np.asarray(value, dtype=float)
            if array.ndim == 2 and array.shape[0] == count:
                result.update({f"{key[len(prefix):]}_{index}": array[:, index] for index in range(array.shape[1])})
            else:
                result[key[len(prefix):]] = _series(value, count, key)
    found = _first_array(arrays, ("contact_found", "found"))
    if not result and found is not None:
        values = np.asarray(found, dtype=float)
        if values.ndim == 1:
            result["contact"] = _series(values, count, "contact_found")
        elif values.ndim == 2 and values.shape[0] == count:
            result = {f"contact_{index}": values[:, index] for index in range(values.shape[1])}
    if not result:
        mapping = _first_value(payload, ("contacts", "contact", "adhesion_outputs"))
        if isinstance(mapping, Mapping):
            result = {
                str(name): _series(value, count, f"contact[{name}]")
                for name, value in mapping.items()
                if np.asarray(value).ndim <= 1
            }
    if not result:
        values = [item.get("contact", item.get("contacts", {})) if isinstance(item, Mapping) else {} for item in frames]
        labels = sorted({str(label) for item in values if isinstance(item, Mapping) for label in item})
        for label in labels:
            samples = []
            for item in values:
                raw = item.get(label) if isinstance(item, Mapping) else None
                array = np.asarray(raw, dtype=float) if raw is not None else np.asarray([], dtype=float)
                samples.append(float(np.any(array > 0.5)) if array.size else 0.0)
            result[label] = _series(samples, count, f"contact[{label}]")
    return result


def _contact_metrics(contacts: Mapping[str, np.ndarray], time_s: np.ndarray, timestep_s: float) -> dict[str, Any]:
    if not contacts:
        return {"available": False, "ratio": {}, "duration_s": {}, "step_frequency_hz": None, "stride_frequency_hz": None}
    duration = max(float(time_s[-1] - time_s[0]), timestep_s) if time_s.size else timestep_s
    ratios: dict[str, float] = {}
    durations: dict[str, float] = {}
    footfalls: dict[str, int] = {}
    for name, values in contacts.items():
        active = np.asarray(values, dtype=float).reshape(-1) > 0.5
        interval_count = min(active.size, time_s.size)
        active = active[:interval_count]
        ratios[name] = _finite_or_none(np.mean(active)) or 0.0
        durations[name] = float(np.count_nonzero(active) * timestep_s)
        footfalls[name] = int(np.count_nonzero(active & ~np.concatenate(([False], active[:-1]))))
    total_steps = sum(footfalls.values())
    per_leg = [value / duration for value in footfalls.values()]
    return {
        "available": True,
        "ratio": ratios,
        "duration_s": durations,
        "step_frequency_hz": float(total_steps / duration),
        "stride_frequency_hz": float(np.mean(per_leg)) if per_leg else None,
    }


def _symmetry_metrics(contacts: Mapping[str, np.ndarray], joint_rms: Mapping[str, float | None]) -> tuple[float | None, dict[str, float]]:
    source = {name: float(value) for name, value in _contact_ratios(contacts).items()}
    if not source:
        source = {name: float(value) for name, value in joint_rms.items() if value is not None}
    pairs = _pair_values(source)
    values = {
        key: float(1.0 - abs(left - right) / (left + right)) if left + right > 0 else 1.0
        for key, (left, right) in pairs.items()
    }
    return (float(np.mean(list(values.values()))) if values else None), values


def _contact_ratios(contacts: Mapping[str, np.ndarray]) -> dict[str, float]:
    return {name: float(np.mean(np.asarray(value, dtype=float) > 0.5)) for name, value in contacts.items()}


def _pair_values(values: Mapping[str, float]) -> dict[str, tuple[float, float]]:
    grouped: dict[str, dict[str, float]] = {}
    for name, value in values.items():
        text = "".join(character for character in str(name).upper() if character.isalnum())
        side = None
        core = text
        if text.startswith("LEFT"):
            side, core = "L", text[4:]
        elif text.startswith("RIGHT"):
            side, core = "R", text[5:]
        elif text.startswith(("L", "R")):
            side, core = text[0], text[1:]
        if side:
            grouped.setdefault(core, {})[side] = value
    return {key: (item["L"], item["R"]) for key, item in grouped.items() if "L" in item and "R" in item}


def _heading_series(quaternions: np.ndarray | None) -> np.ndarray | None:
    if quaternions is None:
        return None
    w, x, y, z = quaternions.T
    return np.unwrap(np.arctan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z)))


def _orientation_series(quaternions: np.ndarray | None) -> dict[str, Any] | None:
    if quaternions is None:
        return None
    w, x, y, z = quaternions.T
    roll = np.arctan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    pitch = np.arcsin(np.clip(2.0 * (w * y - z * x), -1.0, 1.0))
    yaw = np.unwrap(np.arctan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z)))
    variances = {"roll_rad2": float(np.var(roll)), "pitch_rad2": float(np.var(pitch)), "yaw_rad2": float(np.var(yaw))}
    return {
        "variance_rad2": float(np.mean(list(variances.values()))),
        "component_variance_rad2": variances,
        "roll_rad": _json_value(roll),
        "pitch_rad": _json_value(pitch),
        "yaw_rad": _json_value(yaw),
    }


def _curvature_series(heading: np.ndarray | None, step_distance: np.ndarray) -> np.ndarray:
    if heading is None:
        return np.array([], dtype=float)
    delta = np.diff(heading)
    result = np.zeros(heading.size, dtype=float)
    if delta.size:
        result[1:] = np.divide(delta, step_distance, out=np.zeros_like(delta), where=step_distance > 1e-12)
    return result


def _velocity_series(positions: np.ndarray | None, time_s: np.ndarray) -> np.ndarray | None:
    if positions is None:
        return None
    if positions.shape[0] == 1:
        return np.zeros(1, dtype=float)
    return np.concatenate(([0.0], np.linalg.norm(np.diff(positions, axis=0), axis=1) / np.diff(time_s)))


def _rms_by_joint(values: Mapping[str, np.ndarray]) -> dict[str, float]:
    return {name: float(np.sqrt(np.mean(np.square(array)))) for name, array in sorted(values.items())}


def _differentiate(values: Mapping[str, np.ndarray], time_s: np.ndarray) -> dict[str, np.ndarray]:
    return {
        name: np.zeros_like(array) if array.size < 2 else np.gradient(array, time_s, edge_order=1)
        for name, array in values.items()
    }


def _resolve_time(payload: Mapping[str, Any], arrays: Mapping[str, np.ndarray], frames: Sequence[Any], metadata: Mapping[str, Any], count: int) -> tuple[np.ndarray, bool]:
    value = _first_array(arrays, ("time_s", "timestamp_s", "timestamps_s"))
    if value is None:
        value = _first_value(payload, ("time_s", "timestamp_s", "timestamps_s"))
    if value is None and frames:
        values = [item.get("timestamp_s", item.get("time", item.get("timestamp"))) if isinstance(item, Mapping) else None for item in frames]
        if all(item is not None for item in values):
            value = values
    if value is None:
        step = _positive_float(metadata.get("timestep_s", metadata.get("timestep", 1.0)), default=1.0)
        return np.arange(count, dtype=float) * step, True
    time_s = np.asarray(value, dtype=float).reshape(-1)
    if time_s.size != count or not np.isfinite(time_s).all():
        raise ValueError("rollout timestamps must match the trajectory frame count and be finite")
    if time_s.size < 2:
        return np.zeros(count, dtype=float), False
    delta = np.diff(time_s)
    if np.all(delta > 0):
        return time_s, False
    positive = delta[np.isfinite(delta) & (delta > 0)]
    fallback = _positive_float(metadata.get("timestep_s", metadata.get("timestep", 0.0)), default=0.0)
    step = fallback if fallback > 0 else (float(np.median(positive)) if positive.size else 1.0)
    return np.arange(count, dtype=float) * step, True


def _frame_count_hint(payload: Mapping[str, Any], arrays: Mapping[str, np.ndarray], frames: Sequence[Any]) -> int:
    if frames:
        return len(frames)
    for key in ("thorax_positions", "thorax", "positions"):
        if key in arrays:
            return int(np.asarray(arrays[key]).shape[0])
        if key in payload:
            return int(np.asarray(payload[key]).shape[0])
    return 0


def _matrix_to_series(value: Any, names: Sequence[str], count: int, kind: str) -> dict[str, np.ndarray]:
    array = np.asarray(value, dtype=float)
    if array.ndim == 1:
        labels = [names[0] if names else f"joint_0"]
        return {labels[0]: _series(array, count, kind)}
    if array.ndim != 2 or array.shape[0] != count:
        raise ValueError(f"{kind} joint data must have shape (frame_count, joint_count)")
    labels = list(names) if names else [f"joint_{index}" for index in range(array.shape[1])]
    if len(labels) != array.shape[1]:
        raise ValueError("joint_names count does not match joint data width")
    return {label: _series(array[:, index], count, f"{kind}[{label}]") for index, label in enumerate(labels)}


def _series(value: Any, count: int, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float).reshape(-1)
    if array.size != count or not np.isfinite(array).all():
        raise ValueError(f"{name} must contain {count} finite samples")
    return array


def _as_matrix(value: Any, width: int, name: str, count: int | None) -> np.ndarray | None:
    if value is None:
        return None
    array = np.asarray(value, dtype=float)
    if array.ndim == 1 and array.size == width and (count in (None, 1)):
        array = array.reshape(1, width)
    if array.ndim != 2 or array.shape[1] != width or (count is not None and array.shape[0] != count):
        raise ValueError(f"{name} must have shape (frame_count, {width})")
    if not np.isfinite(array).all():
        raise ValueError(f"{name} must contain finite values")
    return array


def _first_array(values: Mapping[str, np.ndarray], names: Sequence[str]) -> np.ndarray | None:
    return next((values[name] for name in names if name in values), None)


def _first_value(values: Mapping[str, Any], names: Sequence[str]) -> Any:
    return next((values[name] for name in names if name in values), None)


def _first_file(root: Path, names: Sequence[str]) -> Path:
    result = _optional_file(root, names)
    if result is None:
        raise FileNotFoundError(f"Required rollout file not found under {root}")
    return result


def _optional_file(root: Path, names: Sequence[str]) -> Path | None:
    return next((root / name for name in names if (root / name).is_file()), None)


def _intervals(time_s: np.ndarray, fallback: float) -> np.ndarray:
    delta = np.diff(time_s)
    return np.where(delta > 0, delta, fallback)


def _positive_float(value: Any, *, default: float) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if np.isfinite(result) and result > 0 else default


def _finite_or_none(value: Any) -> float | None:
    result = float(value)
    return result if np.isfinite(result) else None


def _json_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, np.ndarray):
        return [_json_value(item) for item in value.tolist()]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


__all__ = ["AnalysisResult", "LoadedRollout", "analyze_rollout", "compute_metrics", "load_rollout"]
