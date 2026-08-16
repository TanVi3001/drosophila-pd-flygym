"""Read-only conversion from FlyGym rollout artifacts to viewer poses."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .mesh_exporter import build_mesh_metadata, build_visibility
from .trajectory_exporter import build_trajectory_frames
from .validator import ValidationReport, validate_pose_document


@dataclass(frozen=True)
class RolloutInputs:
    """Source arrays and metadata loaded without changing the dataset."""

    dataset_dir: Path
    rollout_json: Path
    arrays_npz: Path
    metadata: dict[str, Any]
    thorax_positions: np.ndarray
    quaternions: np.ndarray
    quaternion_order: str
    time_s: np.ndarray
    timestep_s: float
    com_positions: np.ndarray | None
    joint_positions: dict[str, np.ndarray]
    joint_velocity: dict[str, np.ndarray]
    joint_acceleration: dict[str, np.ndarray]
    contacts: dict[str, np.ndarray]

    @property
    def frame_count(self) -> int:
        return int(self.thorax_positions.shape[0])


@dataclass(frozen=True)
class PoseExportResult:
    """Output path, source paths and validation report for one export."""

    output_path: Path
    source_files: tuple[Path, Path]
    document: Mapping[str, Any]
    validation: ValidationReport

    def as_dict(self) -> dict[str, Any]:
        return {
            "output": self.output_path.as_posix(),
            "sources": [path.as_posix() for path in self.source_files],
            "frame_count": self.document["frame_count"],
            "validation": self.validation.as_dict(),
        }


def export_viewer_pose(
    dataset: str | Path,
    output_path: str | Path,
    *,
    search_roots: Sequence[str | Path] | None = None,
) -> PoseExportResult:
    """Export ``rollout.json`` and ``rollout_arrays.npz`` as ``viewer_pose.json``."""

    dataset_dir = resolve_dataset(dataset, search_roots=search_roots)
    inputs = load_rollout_inputs(dataset_dir)
    document = build_viewer_pose(inputs)
    validation = validate_pose_document(document, expected_frame_count=inputs.frame_count)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(document, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return PoseExportResult(target, (inputs.rollout_json, inputs.arrays_npz), document, validation)


def resolve_dataset(
    dataset: str | Path,
    *,
    search_roots: Sequence[str | Path] | None = None,
) -> Path:
    """Resolve a dataset path or ID using conventional repository data roots."""

    requested = Path(dataset)
    if requested.is_dir():
        return requested.resolve()
    roots = [Path(root) for root in (search_roots or (Path.cwd(), Path.cwd() / "datasets", Path.cwd() / "research" / "datasets"))]
    candidates = []
    for root in roots:
        candidates.extend((root / str(dataset), root / "healthy" / str(dataset)))
    for candidate in candidates:
        if candidate.is_dir():
            return candidate.resolve()
    raise FileNotFoundError(f"Dataset directory not found: {dataset}")


def load_rollout_inputs(dataset_dir: str | Path) -> RolloutInputs:
    """Load the two required input artifacts from a dataset directory."""

    root = Path(dataset_dir).resolve()
    json_path = _find_input(root, "rollout.json")
    npz_path = _find_input(root, "rollout_arrays.npz")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("rollout.json must contain an object")
    data = payload.get("rollout") if isinstance(payload.get("rollout"), Mapping) else payload
    metadata = dict(data.get("metadata", {})) if isinstance(data.get("metadata"), Mapping) else {}
    with np.load(npz_path, allow_pickle=False) as archive:
        arrays = {key: np.asarray(archive[key]) for key in archive.files}
    frames = data.get("frames") if isinstance(data.get("frames"), Sequence) else []
    positions = _positions(data, arrays, frames)
    quaternions, quaternion_order = _quaternions(data, arrays, frames)
    if positions.shape[0] != quaternions.shape[0]:
        raise ValueError("thorax and orientation frame counts do not match")
    time_s = _time_values(data, arrays, frames, metadata, positions.shape[0])
    timestep_s = _positive_timestep(
        time_s,
        fallback=_explicit_timestep(data, arrays, metadata),
    )
    metadata.setdefault("timestep_s", timestep_s)
    joint_names = _joint_names(data, metadata)
    joint_positions = _joint_series(data, arrays, frames, positions.shape[0], joint_names, "angle")
    joint_velocity = _joint_series(data, arrays, frames, positions.shape[0], joint_names, "velocity")
    joint_acceleration = _joint_series(data, arrays, frames, positions.shape[0], joint_names, "acceleration")
    if not joint_velocity and joint_positions:
        joint_velocity = _differentiate(joint_positions, timestep_s)
    if not joint_acceleration and joint_velocity:
        joint_acceleration = _differentiate(joint_velocity, timestep_s)
    com = _com_values(data, arrays, frames, positions.shape[0])
    contacts = _contact_series(data, arrays, frames, positions.shape[0])
    metadata.update({
        "dataset_id": metadata.get("dataset_id", root.name),
        "source_rollout_json": json_path.name,
        "source_arrays_npz": npz_path.name,
        "quaternion_order": "xyzw",
        "input_quaternion_order": quaternion_order,
    })
    return RolloutInputs(
        dataset_dir=root,
        rollout_json=json_path,
        arrays_npz=npz_path,
        metadata=_json_safe(metadata),
        thorax_positions=positions,
        quaternions=quaternions,
        quaternion_order=quaternion_order,
        time_s=time_s,
        timestep_s=timestep_s,
        com_positions=com,
        joint_positions=joint_positions,
        joint_velocity=joint_velocity,
        joint_acceleration=joint_acceleration,
        contacts=contacts,
    )


def build_viewer_pose(inputs: RolloutInputs) -> dict[str, Any]:
    """Build a deterministic, JSON-ready viewer pose document."""

    positions = np.asarray(inputs.thorax_positions, dtype=float)
    quaternions = _to_xyzw(inputs.quaternions, inputs.quaternion_order)
    joint_names = sorted(set(inputs.joint_positions) | set(inputs.joint_velocity) | set(inputs.joint_acceleration))
    visibility = build_visibility(
        has_joint_data=bool(joint_names),
        has_com_data=inputs.com_positions is not None,
    )
    trajectories = build_trajectory_frames(
        positions,
        com_positions=inputs.com_positions,
        joint_positions=inputs.joint_positions,
    )
    frames = []
    for index in range(inputs.frame_count):
        com = None if inputs.com_positions is None else _json_safe(inputs.com_positions[index])
        angles = _frame_joint_values(inputs.joint_positions, index)
        velocity = _frame_joint_values(inputs.joint_velocity, index)
        acceleration = _frame_joint_values(inputs.joint_acceleration, index)
        contact = _frame_contact_values(inputs.contacts, index)
        frames.append({
            "frame_index": index,
            "time": float(inputs.time_s[index]),
            "thorax": _json_safe(positions[index]),
            "position": _json_safe(positions[index]),
            "orientation": _json_safe(quaternions[index]),
            "COM": com,
            "joint_angles": angles,
            "joint_velocity": velocity,
            "joint_velocities": velocity,
            "joint_acceleration": acceleration,
            "contacts": contact,
            "trajectory": trajectories[index],
            "visibility": dict(visibility),
        })
    metadata = {
        **inputs.metadata,
        "schema_version": "viewer-pose-1.0",
        "quaternion_order": "xyzw",
        "scientific_scope": (
            "Computational visualization interchange generated from imported rollout arrays; "
            "not biological validation."
        ),
    }
    return {
        "metadata": _json_safe(metadata),
        "fps": float(1.0 / inputs.timestep_s),
        "frame_count": inputs.frame_count,
        "joint_names": joint_names,
        "mesh": build_mesh_metadata(joint_names=joint_names, visibility=visibility),
        "frames": frames,
    }


def _find_input(root: Path, name: str) -> Path:
    fallback_names = ("rollout.npz",) if name == "rollout_arrays.npz" else ()
    candidates = (
        root / name,
        root / "rollouts" / name,
        *(root / fallback for fallback in fallback_names),
        *(root / "rollouts" / fallback for fallback in fallback_names),
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"Required input {name!r} not found under {root}")


def _positions(data: Mapping[str, Any], arrays: Mapping[str, np.ndarray], frames: Sequence[Any]) -> np.ndarray:
    value = _first_array(arrays, ("thorax_positions", "thorax_positions_mm", "thorax", "positions"))
    if value is None:
        value = _first_value(data, ("thorax_positions", "thorax_positions_mm", "thorax", "positions"))
    if value is None and frames:
        value = [frame.get("thorax", frame.get("position")) if isinstance(frame, Mapping) else None for frame in frames]
    return _matrix("thorax_positions", value, 3)


def _quaternions(data: Mapping[str, Any], arrays: Mapping[str, np.ndarray], frames: Sequence[Any]) -> tuple[np.ndarray, str]:
    for key in ("thorax_quaternions_xyzw", "quaternions_xyzw"):
        if key in arrays:
            return _matrix("thorax_quaternions", arrays[key], 4), "xyzw"
    for key in ("thorax_quaternions", "quaternions", "orientation"):
        if key in arrays:
            return _matrix("thorax_quaternions", arrays[key], 4), "wxyz"
    for key in ("thorax_quaternions_xyzw", "quaternions_xyzw"):
        value = data.get(key)
        if value is not None:
            return _matrix("thorax_quaternions", value, 4), "xyzw"
    value = _first_value(data, ("thorax_quaternions", "quaternions", "orientation"))
    if value is not None:
        return _matrix("thorax_quaternions", value, 4), "wxyz"
    values = []
    order = "wxyz"
    for frame in frames:
        item = frame.get("orientation") if isinstance(frame, Mapping) else None
        if isinstance(item, Mapping) and all(key in item for key in ("qx", "qy", "qz", "qw")):
            values.append([item["qx"], item["qy"], item["qz"], item["qw"]])
            order = "xyzw"
        else:
            values.append(item)
    return _matrix("thorax_quaternions", values, 4), order


def _time_values(
    data: Mapping[str, Any],
    arrays: Mapping[str, np.ndarray],
    frames: Sequence[Any],
    metadata: Mapping[str, Any],
    count: int,
) -> np.ndarray:
    value = _first_array(arrays, ("time_s", "timestamp_s", "timestamps_s"))
    if value is None:
        value = _first_value(data, ("time_s", "timestamp_s", "timestamps_s"))
    if value is None and frames:
        values = [frame.get("time", frame.get("timestamp_s", frame.get("timestamp"))) if isinstance(frame, Mapping) else None for frame in frames]
        if all(item is not None for item in values):
            value = values
    if value is None:
        timestep = _first_array(arrays, ("timestep_s", "timestep"))
        if timestep is None:
            timestep = _first_value(data, ("timestep_s", "timestep"))
        if timestep is None:
            timestep = metadata.get("timestep_s", metadata.get("timestep"))
        if timestep is None:
            raise ValueError("rollout requires time_s or a positive timestep_s")
        step = float(np.asarray(timestep, dtype=float).ravel()[0])
        if not np.isfinite(step) or step <= 0:
            raise ValueError("timestep_s must be positive and finite")
        value = np.arange(count, dtype=float) * step
    result = np.asarray(value, dtype=float).reshape(-1)
    if result.shape[0] != count:
        raise ValueError("time and trajectory frame counts do not match")
    return result


def _explicit_timestep(
    data: Mapping[str, Any],
    arrays: Mapping[str, np.ndarray],
    metadata: Mapping[str, Any],
) -> float | None:
    value = _first_array(arrays, ("timestep_s", "timestep"))
    if value is None:
        value = _first_value(data, ("timestep_s", "timestep"))
    if value is None:
        value = metadata.get("timestep_s", metadata.get("timestep"))
    if value is None:
        return None
    candidate = float(np.asarray(value, dtype=float).reshape(-1)[0])
    return candidate if np.isfinite(candidate) and candidate > 0 else None


def _positive_timestep(time_s: np.ndarray, *, fallback: float | None = None) -> float:
    if time_s.size < 2:
        value = 1.0 if fallback is None else float(fallback)
    else:
        deltas = np.diff(time_s)
        if not np.isfinite(deltas).all() or not np.all(deltas > 0) or not np.allclose(deltas, deltas[0]):
            raise ValueError("time_s must be strictly increasing with a constant timestep")
        value = float(deltas[0])
    if not np.isfinite(value) or value <= 0:
        raise ValueError("timestep_s must be positive and finite")
    return value


def _com_values(data: Mapping[str, Any], arrays: Mapping[str, np.ndarray], frames: Sequence[Any], count: int) -> np.ndarray | None:
    value = _first_array(arrays, ("com_positions", "com_positions_mm", "com"))
    if value is None:
        value = _first_value(data, ("com_positions", "com_positions_mm", "com", "COM"))
    if value is None and frames:
        values = [frame.get("com", frame.get("COM")) if isinstance(frame, Mapping) else None for frame in frames]
        if any(item is not None for item in values):
            value = values
    if value is None:
        return None
    return _matrix("com_positions", value, 3, expected_count=count)


def _joint_names(data: Mapping[str, Any], metadata: Mapping[str, Any]) -> list[str]:
    for source in (data.get("joint_names"), metadata.get("joint_names")):
        if isinstance(source, Sequence) and not isinstance(source, (str, bytes)):
            return [str(item) for item in source]
    return []


def _joint_series(
    data: Mapping[str, Any],
    arrays: Mapping[str, np.ndarray],
    frames: Sequence[Any],
    count: int,
    names: list[str],
    kind: str,
) -> dict[str, np.ndarray]:
    result: dict[str, np.ndarray] = {}
    prefixes = {"angle": ("joint__",), "velocity": ("joint_velocity__", "joint_velocities__"), "acceleration": ("joint_acceleration__", "joint_accelerations__")}[kind]
    for key, value in arrays.items():
        prefix = next((item for item in prefixes if key.startswith(item)), None)
        if prefix:
            result[key[len(prefix):]] = _series_array(value, count, key)
    matrix_keys = {"angle": ("joint_positions", "joint_angles"), "velocity": ("joint_velocity", "joint_velocities"), "acceleration": ("joint_acceleration", "joint_accelerations")}[kind]
    matrix = _first_array(arrays, matrix_keys)
    if matrix is not None and not result:
        result.update(_matrix_to_joint_series(matrix, names, count, kind))
    field_keys = {"angle": ("joint_angles", "joint_positions"), "velocity": ("joint_velocity", "joint_velocities"), "acceleration": ("joint_acceleration", "joint_accelerations")}[kind]
    value = _first_value(data, field_keys)
    if value is not None and not result:
        result.update(_value_to_joint_series(value, names, count, kind))
    if frames and not result:
        result.update(_frames_to_joint_series(frames, names, count, field_keys))
    return result


def _matrix_to_joint_series(value: Any, names: list[str], count: int, kind: str) -> dict[str, np.ndarray]:
    array = np.asarray(value, dtype=float)
    if array.ndim == 1:
        return {names[0] if names else f"joint_0": _series_array(array, count, f"{kind}[0]")}
    if array.ndim < 2 or array.shape[0] != count:
        raise ValueError(f"{kind} joint array must have frame dimension {count}")
    width = array.shape[1]
    labels = names or [f"joint_{index}" for index in range(width)]
    if len(labels) != width:
        raise ValueError("joint_names count does not match joint array width")
    return {name: _series_array(array[:, index], count, f"{kind}[{name}]") for index, name in enumerate(labels)}


def _value_to_joint_series(value: Any, names: list[str], count: int, kind: str) -> dict[str, np.ndarray]:
    if isinstance(value, Mapping):
        return {str(name): _series_array(series, count, f"{kind}[{name}]") for name, series in value.items()}
    return _matrix_to_joint_series(value, names, count, kind)


def _frames_to_joint_series(frames: Sequence[Any], names: list[str], count: int, keys: Sequence[str]) -> dict[str, np.ndarray]:
    values = [next((frame.get(key) for key in keys if isinstance(frame, Mapping) and key in frame), None) for frame in frames]
    if not any(item is not None for item in values):
        return {}
    if all(isinstance(item, Mapping) for item in values):
        labels = sorted({str(name) for item in values for name in item})
        return {name: _series_array([item.get(name) for item in values], count, name) for name in labels}
    return _matrix_to_joint_series(values, names, count, "joint")


def _differentiate(series: Mapping[str, np.ndarray], timestep: float) -> dict[str, np.ndarray]:
    return {name: np.gradient(value, timestep, axis=0, edge_order=1) if value.shape[0] > 1 else np.zeros_like(value) for name, value in series.items()}


def _contact_series(data: Mapping[str, Any], arrays: Mapping[str, np.ndarray], frames: Sequence[Any], count: int) -> dict[str, np.ndarray]:
    result = {}
    for key, value in arrays.items():
        if key.startswith("adhesion__"):
            result[key[len("adhesion__"):]] = _series_array(value, count, key)
        elif key.startswith("contact__"):
            result[key[len("contact__"):]] = _series_array(value, count, key)
    if result:
        return result
    values = [frame.get("contact", frame.get("contacts", {})) if isinstance(frame, Mapping) else {} for frame in frames]
    labels = sorted({str(name) for item in values if isinstance(item, Mapping) for name in item})
    return {name: _series_array([item.get(name) if isinstance(item, Mapping) else None for item in values], count, f"contact[{name}]") for name in labels}


def _frame_joint_values(series: Mapping[str, np.ndarray], index: int) -> dict[str, Any]:
    return {name: _json_safe(value[index]) for name, value in sorted(series.items())}


def _frame_contact_values(series: Mapping[str, np.ndarray], index: int) -> dict[str, Any]:
    return {name: _json_safe(value[index]) for name, value in sorted(series.items())}


def _first_array(values: Mapping[str, np.ndarray], names: Sequence[str]) -> np.ndarray | None:
    return next((values[name] for name in names if name in values), None)


def _first_value(values: Mapping[str, Any], names: Sequence[str]) -> Any:
    return next((values[name] for name in names if name in values), None)


def _matrix(name: str, value: Any, width: int, *, expected_count: int | None = None) -> np.ndarray:
    if value is None:
        raise ValueError(f"rollout is missing {name}")
    array = np.asarray(value, dtype=float)
    if array.ndim != 2 or array.shape[1] != width:
        raise ValueError(f"{name} must have shape (n_samples, {width})")
    if expected_count is not None and array.shape[0] != expected_count:
        raise ValueError(f"{name} frame count does not match thorax positions")
    return array


def _series_array(value: Any, count: int, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim == 0:
        raise ValueError(f"{name} must contain one value per frame")
    if array.shape[0] != count:
        raise ValueError(f"{name} frame count does not match rollout")
    return array


def _to_xyzw(value: np.ndarray, order: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if order == "wxyz":
        array = array[:, [1, 2, 3, 0]]
    norms = np.linalg.norm(array, axis=1)
    if not np.isfinite(norms).all() or np.any(norms <= 0):
        raise ValueError("quaternions must be finite and non-zero")
    return array / norms[:, None]


def _json_safe(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


__all__ = ["PoseExportResult", "RolloutInputs", "build_viewer_pose", "export_viewer_pose", "load_rollout_inputs", "resolve_dataset"]
