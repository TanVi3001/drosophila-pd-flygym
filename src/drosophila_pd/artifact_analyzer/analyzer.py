"""Inspect stored research artifacts without running scientific code.

The analyzer deliberately treats missing material as a reportable state. It
does not generate rollouts, infer unavailable metrics, or turn qualitative
literature into numeric targets.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from drosophila_pd.analysis.rollout_analysis import LoadedRollout, load_rollout


WAITING_RUNTIME = "WAITING_RUNTIME"
WAITING_DATASET = "WAITING_DATASET"
WAITING_TARGET_DATA = "WAITING_TARGET_DATA"
PASS = "PASS"
FAILED = "FAILED"

OUTPUT_NAMES = (
    "artifact_summary.md",
    "artifact_summary.json",
    "integrity_report.csv",
    "dataset_report.csv",
    "metric_report.csv",
    "campaign_report.csv",
    "calibration_readiness.csv",
    "validation_readiness.csv",
)

METRIC_DEFINITIONS: dict[str, tuple[tuple[str, ...], str | None]] = {
    "walking_speed_mm_s": (("walking_speed_mm_s", "mean_planar_speed_mm_s", "walking_speed"), "nonnegative"),
    "path_length_mm": (("total_distance_mm", "planar_path_length_mm", "path_length_mm"), "nonnegative"),
    "trajectory_efficiency": (("trajectory_efficiency",), "unit_interval"),
    "com_displacement_mm": (("com_displacement_mm", "com_displacement"), "nonnegative"),
    "heading_variance_rad2": (("heading_variance_rad2", "heading_variance", "heading_yaw_variance_rad2"), "nonnegative"),
    "pause_fraction": (("pause_fraction", "immobility_ratio"), "unit_interval"),
    "joint_velocity": (("joint_velocity", "joint_rms_velocity", "joint_velocity_rms"), "nonnegative"),
    "symmetry_index": (("symmetry_index",), "unit_interval"),
    "orientation_stability": (("orientation_stability", "body_orientation_variance_rad2", "orientation_variance_rad2"), "nonnegative"),
}


@dataclass(frozen=True)
class ArtifactAnalysisResult:
    """Paths and summary returned by :func:`analyze_artifacts`."""

    summary: dict[str, Any]
    output_dir: Path
    files: dict[str, Path]


def analyze_artifacts(
    *,
    repo_root: str | Path | None = None,
    results_dir: str | Path = "results",
    datasets_dir: str | Path = "datasets",
    paper_dir: str | Path = "paper",
    metrics_dir: str | Path = "metrics",
    campaign_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    check_runtime: bool = True,
) -> ArtifactAnalysisResult:
    """Analyze existing artifacts and write a deterministic report package.

    Paths are resolved relative to ``repo_root``. ``WAITING_*`` states are
    successful audit outcomes: they describe what is not yet available and do
    not cause the CLI to fabricate replacement data.
    """

    root = Path(repo_root or Path.cwd()).expanduser().resolve()
    results = _resolve(root, results_dir)
    datasets = _resolve(root, datasets_dir)
    paper = _resolve(root, paper_dir)
    metrics = _resolve(root, metrics_dir)
    output = _resolve(root, output_dir or results / "artifact_analysis")

    runtime_status, runtime_detail = _runtime_gate(root) if check_runtime else (PASS, {"checked": False})
    dataset_dirs = _discover_datasets(datasets)
    integrity_rows: list[dict[str, Any]] = []
    dataset_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []
    duplicate_groups = _duplicate_rollouts(dataset_dirs)

    loaded: dict[str, LoadedRollout] = {}
    for dataset in dataset_dirs:
        integrity = _inspect_integrity(dataset, duplicate_groups.get(dataset))
        integrity_rows.extend(integrity)
        dataset_row, rollout = _inspect_dataset(dataset)
        dataset_rows.append(dataset_row)
        if rollout is not None:
            loaded[dataset.name] = rollout
        metric_rows.extend(_inspect_metrics(dataset, rollout, metrics))

    campaign = _inspect_campaign(root, results, campaign_path)
    calibration = _inspect_calibration(root, loaded, metrics)
    validation = _inspect_validation(root, paper, loaded, calibration["target_available"])

    hard_dataset_failure = any(row["status"] == FAILED for row in dataset_rows)
    if runtime_status != PASS:
        overall_status = WAITING_RUNTIME
    elif not dataset_dirs:
        overall_status = WAITING_DATASET
    elif not calibration["target_available"]:
        overall_status = WAITING_TARGET_DATA
    elif hard_dataset_failure:
        overall_status = FAILED
    else:
        overall_status = PASS

    summary = {
        "status": overall_status,
        "generated_at": datetime.now(UTC).isoformat(),
        "scientific_scope": (
            "Artifact integrity and computational readiness review only; "
            "not biological validation, diagnosis, clinical prediction, or drug response."
        ),
        "inputs": {
            "results": str(results),
            "datasets": str(datasets),
            "paper": str(paper),
            "metrics": str(metrics),
            "campaign": campaign["path"],
        },
        "runtime": {"status": runtime_status, **runtime_detail},
        "datasets": {
            "count": len(dataset_dirs),
            "valid_count": sum(row["status"] == PASS for row in dataset_rows),
            "failed_count": sum(row["status"] == FAILED for row in dataset_rows),
        },
        "campaign": campaign,
        "calibration": calibration,
        "validation": validation,
        "warnings": _warnings(dataset_rows, metric_rows, campaign, validation),
    }
    output.mkdir(parents=True, exist_ok=True)
    tables = {
        "integrity_report.csv": integrity_rows or [_empty_row("integrity", overall_status)],
        "dataset_report.csv": dataset_rows or [_empty_row("dataset", overall_status)],
        "metric_report.csv": metric_rows or [_empty_row("metric", overall_status)],
        "campaign_report.csv": campaign["rows"],
        "calibration_readiness.csv": [calibration],
        "validation_readiness.csv": [validation],
    }
    files: dict[str, Path] = {}
    for name, rows in tables.items():
        path = output / name
        _write_csv(path, rows)
        files[name] = path
    summary_path = output / "artifact_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    files[summary_path.name] = summary_path
    markdown_path = output / "artifact_summary.md"
    markdown_path.write_text(_summary_markdown(summary), encoding="utf-8")
    files[markdown_path.name] = markdown_path
    return ArtifactAnalysisResult(summary=summary, output_dir=output, files=files)


def _resolve(root: Path, value: str | Path) -> Path:
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _runtime_gate(root: Path) -> tuple[str, dict[str, Any]]:
    checker_path = root / "scripts" / "check_runtime.py"
    if not checker_path.is_file():
        return WAITING_RUNTIME, {"checked": False, "reason": "scripts/check_runtime.py is missing"}
    try:
        source = str(root / "src")
        if source not in sys.path:
            sys.path.insert(0, source)
        spec = importlib.util.spec_from_file_location("_artifact_runtime_check", checker_path)
        if spec is None or spec.loader is None:
            raise ImportError("could not load runtime checker")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        report = module.check_runtime(root)
        return (PASS if report.runtime_ready else WAITING_RUNTIME), report.as_dict()
    except Exception as exc:  # A broken environment is a waiting state, not an analyzer crash.
        return WAITING_RUNTIME, {"checked": False, "reason": f"{type(exc).__name__}: {exc}"}


def _discover_datasets(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    candidates: set[Path] = set()
    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        names = {item.name for item in path.iterdir() if item.is_file()}
        if {"rollout.json", "rollout.npz", "rollout_arrays.npz"} & names or {"manifest.json", "dataset_manifest.json"} & names:
            candidates.add(path.resolve())
    return sorted(candidates, key=lambda item: item.as_posix())


def _duplicate_rollouts(datasets: Sequence[Path]) -> dict[Path, str]:
    hashes: dict[str, list[Path]] = {}
    for dataset in datasets:
        source = _first_file(dataset, ("rollout.json", "rollout.npz", "rollout_arrays.npz"))
        if source is not None:
            hashes.setdefault(_sha256(source), []).append(dataset)
    return {
        dataset: digest
        for digest, paths in hashes.items()
        if len(paths) > 1
        for dataset in paths
    }


def _inspect_integrity(dataset: Path, duplicate_hash: str | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    manifest_path = _first_file(dataset, ("manifest.json", "dataset_manifest.json"))
    rows.append(_integrity_row(dataset, "manifest", manifest_path.name if manifest_path else "manifest.json", "PRESENT" if manifest_path else "MISSING"))
    metadata_path = dataset / "metadata.json"
    rows.append(_integrity_row(dataset, "required_file", "metadata.json", "PRESENT" if metadata_path.is_file() else "MISSING"))
    rollout = _first_file(dataset, ("rollout.json", "rollout.npz", "rollout_arrays.npz"))
    rows.append(_integrity_row(dataset, "required_file", "rollout.json or rollout.npz", "PRESENT" if rollout else "MISSING"))
    viewer = dataset / "viewer_pose.json"
    rows.append(_integrity_row(dataset, "optional_file", "viewer_pose.json", "PRESENT" if viewer.is_file() else "MISSING_OPTIONAL"))
    metrics = _find_metric_files(dataset, dataset.parent)
    rows.append(_integrity_row(dataset, "optional_file", "metrics.json", "PRESENT" if metrics else "MISSING_OPTIONAL"))
    if duplicate_hash:
        rows.append(_integrity_row(dataset, "duplicate_rollout", rollout.name if rollout else "", "DUPLICATE", duplicate_hash))
    if manifest_path is None:
        return rows
    try:
        manifest = _read_json(manifest_path)
        declared = _manifest_files(manifest)
        if not declared:
            rows.append(_integrity_row(dataset, "checksum", manifest_path.name, "UNAVAILABLE", "manifest has no file hashes"))
        for relative, expected in declared.items():
            target = (dataset / relative).resolve()
            safe = target == dataset.resolve() or dataset.resolve() in target.parents
            if not safe:
                rows.append(_integrity_row(dataset, "manifest_path", relative, FAILED, "path escapes dataset"))
                continue
            if not target.is_file():
                rows.append(_integrity_row(dataset, "manifest_file", relative, "MISSING"))
                continue
            actual = _sha256(target)
            status = PASS if expected is None or actual == expected else FAILED
            rows.append(_integrity_row(dataset, "checksum", relative, status, actual if expected is None else f"expected={expected}; actual={actual}"))
        checksum_file = dataset / "checksums.sha256"
        if checksum_file.is_file():
            for relative, expected in _read_checksum_file(checksum_file).items():
                target = (dataset / relative).resolve()
                actual = _sha256(target) if target.is_file() else None
                rows.append(_integrity_row(dataset, "checksum_file", relative, PASS if actual == expected else FAILED, f"expected={expected}; actual={actual}"))
    except Exception as exc:
        rows.append(_integrity_row(dataset, "manifest_parse", manifest_path.name, FAILED, f"{type(exc).__name__}: {exc}"))
    return rows


def _inspect_dataset(dataset: Path) -> tuple[dict[str, Any], LoadedRollout | None]:
    row: dict[str, Any] = {
        "dataset_id": dataset.name,
        "path": str(dataset),
        "status": PASS,
        "sample_count": None,
        "expected_sample_count": None,
        "sample_count_consistent": "UNAVAILABLE",
        "timestep_s": None,
        "timestep_consistent": "UNAVAILABLE",
        "duration_s": None,
        "expected_duration_s": None,
        "duration_consistent": "UNAVAILABLE",
        "nan_count": None,
        "inf_count": None,
        "timestamp_monotonic": "UNAVAILABLE",
        "timestamps_reconstructed": False,
        "details": "",
    }
    try:
        rollout = load_rollout(dataset)
        raw_time, reconstructed = _raw_time(dataset, rollout)
        row.update({
            "sample_count": rollout.frame_count,
            "timestep_s": rollout.timestep_s,
            "duration_s": float(rollout.time_s[-1] - rollout.time_s[0]) if rollout.time_s.size > 1 else 0.0,
            "timestamps_reconstructed": reconstructed or rollout.timestamps_reconstructed,
        })
        expected_frame = _metadata_number(rollout.metadata, ("frame_count", "sample_count"))
        expected_duration = _metadata_number(rollout.metadata, ("executed_duration_s", "duration_s", "requested_duration_s", "duration"))
        row["expected_sample_count"] = expected_frame
        row["expected_duration_s"] = expected_duration
        row["sample_count_consistent"] = expected_frame is None or int(expected_frame) == rollout.frame_count
        row["timestep_consistent"] = _timestep_consistency(raw_time)
        row["duration_consistent"] = expected_duration is None or bool(np.isclose(row["duration_s"], expected_duration, rtol=1e-5, atol=1e-9))
        row["timestamp_monotonic"] = bool(raw_time.size < 2 or np.all(np.diff(raw_time) > 0))
        arrays = _rollout_arrays(rollout)
        row["nan_count"] = int(sum(np.isnan(value).sum() for value in arrays))
        row["inf_count"] = int(sum(np.isinf(value).sum() for value in arrays))
        checks = (row["sample_count_consistent"], row["timestep_consistent"], row["duration_consistent"], row["timestamp_monotonic"], row["nan_count"] == 0, row["inf_count"] == 0)
        if not all(value is True for value in checks):
            row["status"] = FAILED
            row["details"] = "One or more dataset consistency checks failed."
        return row, rollout
    except Exception as exc:
        row["status"] = FAILED
        row["details"] = f"{type(exc).__name__}: {exc}"
        return row, None


def _inspect_metrics(dataset: Path, rollout: LoadedRollout | None, metrics_root: Path) -> list[dict[str, Any]]:
    payload: dict[str, Any] = {}
    files = _find_metric_files(dataset, metrics_root)
    for path in files:
        try:
            raw = _read_json(path)
            if isinstance(raw, Mapping):
                payload.update(_flatten_scalars(raw))
        except Exception:
            continue
    rows: list[dict[str, Any]] = []
    for name, (aliases, expected_range) in METRIC_DEFINITIONS.items():
        source_key = next((alias for alias in aliases if alias in payload), None)
        value = payload.get(source_key) if source_key else None
        status, finite, range_status, details = _metric_status(value, expected_range, bool(files))
        rows.append({
            "dataset_id": dataset.name,
            "metric": name,
            "status": status,
            "source": source_key or "",
            "value": _cell(value),
            "finite": finite,
            "range_status": range_status,
            "details": details,
        })
    return rows


def _metric_status(value: Any, expected_range: str | None, has_file: bool) -> tuple[str, str, str, str]:
    if value is None or (isinstance(value, str) and value.strip().upper() in {"UNAVAILABLE", "UNAVAILABLE_METRIC", "NONE", "NULL"}):
        return ("UNAVAILABLE_METRIC" if has_file else "MISSING_METRIC", "", "", "Metric is unavailable; no value was inferred.")
    numeric = _numeric_values(value)
    if not numeric:
        return "INVALID_METRIC", "False", "INVALID", "Metric is not numeric."
    finite = all(np.isfinite(item) for item in numeric)
    if not finite:
        return "INVALID_METRIC", "False", "INVALID", "Metric contains NaN or Inf."
    if expected_range == "unit_interval" and any(item < 0 or item > 1 for item in numeric):
        return "INVALID_METRIC", "True", "OUT_OF_RANGE", "Expected values in [0, 1]."
    if expected_range == "nonnegative" and any(item < 0 for item in numeric):
        return "INVALID_METRIC", "True", "OUT_OF_RANGE", "Expected non-negative values."
    return PASS, "True", "PASS", ""


def _inspect_campaign(root: Path, results: Path, campaign_path: str | Path | None) -> dict[str, Any]:
    candidates = []
    if campaign_path is not None:
        candidates.append(_resolve(root, campaign_path))
    candidates.extend([results / "experimental_campaign" / "campaign_data.json", results / "campaign_data.json", root / "campaign_data.json"])
    path = next((item for item in candidates if item.is_file()), None)
    if path is None:
        row = {"campaign_id": "", "status": "MISSING_CAMPAIGN_DATA", "completed": 0, "failed": 0, "skipped": 0, "waiting": 0, "total": 0, "path": "", "details": "campaign_data.json was not found."}
        return {"path": "", "status": "MISSING_CAMPAIGN_DATA", "completed": 0, "failed": 0, "skipped": 0, "waiting": 0, "total": 0, "rows": [row]}
    try:
        payload = _read_json(path)
        records = _campaign_records(payload)
        counts = {name: 0 for name in ("completed", "failed", "skipped", "waiting")}
        for record in records:
            normalized = _normalize_status(record.get("status"))
            if normalized in counts:
                counts[normalized] += 1
        status = FAILED if counts["failed"] else PASS
        row = {"campaign_id": str(payload.get("campaign_name", payload.get("campaign_id", path.stem))), "status": status, **counts, "total": sum(counts.values()), "path": str(path), "details": ""}
        return {"path": str(path), "status": status, **counts, "total": row["total"], "rows": [row]}
    except Exception as exc:
        row = {"campaign_id": path.stem, "status": FAILED, "completed": 0, "failed": 0, "skipped": 0, "waiting": 0, "total": 0, "path": str(path), "details": f"{type(exc).__name__}: {exc}"}
        return {"path": str(path), "status": FAILED, "completed": 0, "failed": 0, "skipped": 0, "waiting": 0, "total": 0, "rows": [row]}


def _inspect_calibration(root: Path, loaded: Mapping[str, LoadedRollout], metrics_root: Path) -> dict[str, Any]:
    candidates = [
        root / "research" / "campaign" / "calibration_targets.csv",
        root / "research" / "calibration_targets.csv",
        root / "research" / "phenotype_atlas" / "phenotype_database.json",
        root / "configs" / "parkinson" / "phenotype_database.json",
    ]
    target = next((path for path in candidates if path.is_file()), None)
    available = bool(target and _has_numeric_target(target))
    status = PASS if available and loaded else (WAITING_TARGET_DATA if not available else WAITING_DATASET)
    return {
        "target_path": str(target) if target else "",
        "target_available": available,
        "dataset_available": bool(loaded),
        "metrics_available": bool(loaded),
        "calibration_possible": bool(available and loaded),
        "status": status,
        "details": "Numeric approved/usable target data is required; template rows do not count." if not available else "",
    }


def _inspect_validation(root: Path, paper: Path, loaded: Mapping[str, LoadedRollout], targets_available: bool) -> dict[str, Any]:
    atlas = root / "research" / "phenotype_atlas"
    literature_available = _has_literature(paper, atlas)
    holdout = len(loaded) >= 2
    status = PASS if literature_available and holdout and targets_available else "WAITING_VALIDATION_DATA"
    return {
        "literature_available": literature_available,
        "holdout_possible": holdout,
        "target_available": targets_available,
        "dataset_count": len(loaded),
        "status": status,
        "details": "Requires literature evidence, usable targets, and at least two valid datasets for a holdout." if status != PASS else "",
    }


def _has_numeric_target(path: Path) -> bool:
    try:
        if path.suffix.lower() == ".csv":
            with path.open(newline="", encoding="utf-8-sig") as handle:
                rows = list(csv.DictReader(handle))
            for row in rows:
                value = next((row.get(key) for key in ("literature value", "value", "target", "mean") if row.get(key)), None)
                if value is not None and _numeric_values(value):
                    return True
            return False
        raw = _read_json(path)
        values = raw if isinstance(raw, list) else raw.get("targets", []) if isinstance(raw, Mapping) else []
        return any(_numeric_values(item.get("value")) for item in values if isinstance(item, Mapping))
    except Exception:
        return False


def _has_literature(paper: Path, atlas: Path) -> bool:
    if paper.is_dir() and any(path.is_file() and path.stat().st_size > 0 for path in paper.rglob("*") if path.suffix.lower() in {".pdf", ".md", ".txt"}):
        return True
    for path in atlas.rglob("*") if atlas.is_dir() else ():
        if not path.is_file() or path.stat().st_size == 0:
            continue
        try:
            raw = _read_json(path) if path.suffix.lower() == ".json" else None
            if isinstance(raw, list) and raw:
                return True
            if isinstance(raw, Mapping) and any(isinstance(value, list) and value for value in raw.values()):
                return True
        except Exception:
            continue
    return False


def _campaign_records(payload: Any) -> list[Mapping[str, Any]]:
    if not isinstance(payload, Mapping):
        return []
    records: list[Mapping[str, Any]] = []
    for key in ("records", "experiments", "conditions", "baseline", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            records.extend(item for item in value if isinstance(item, Mapping))
    return records


def _normalize_status(value: Any) -> str:
    text = str(value or "").strip().upper()
    if text in {"PASS", "COMPLETED", "COMPLETE", "SUCCESS"}:
        return "completed"
    if text in {"FAILED", "FAIL", "ERROR"}:
        return "failed"
    if text in {"SKIPPED", "SKIP"}:
        return "skipped"
    if text.startswith("WAITING") or text in {"QUEUED", "PENDING"}:
        return "waiting"
    return "skipped" if text else "waiting"


def _raw_time(dataset: Path, rollout: LoadedRollout) -> tuple[np.ndarray, bool]:
    json_path = dataset / "rollout.json"
    if json_path.is_file():
        raw = _read_json(json_path)
        payload = raw.get("rollout", raw) if isinstance(raw, Mapping) else {}
        frames = payload.get("frames", []) if isinstance(payload, Mapping) else []
        values = [item.get("timestamp_s", item.get("time", item.get("timestamp"))) for item in frames if isinstance(item, Mapping)]
        if values and len(values) == len(frames) and all(value is not None for value in values):
            return np.asarray(values, dtype=float), False
        for key in ("time_s", "timestamp_s", "timestamps_s"):
            if isinstance(payload, Mapping) and key in payload:
                return np.asarray(payload[key], dtype=float).reshape(-1), False
    for name in ("rollout.npz", "rollout_arrays.npz"):
        path = dataset / name
        if path.is_file():
            with np.load(path, allow_pickle=False) as archive:
                for key in ("time_s", "timestamp_s", "timestamps_s"):
                    if key in archive:
                        return np.asarray(archive[key], dtype=float).reshape(-1), False
    return np.arange(rollout.frame_count, dtype=float) * rollout.timestep_s, True


def _timestep_consistency(time_s: np.ndarray) -> bool | str:
    if time_s.size < 3:
        return True
    delta = np.diff(time_s)
    if not np.isfinite(delta).all() or np.any(delta <= 0):
        return False
    return bool(np.allclose(delta, np.median(delta), rtol=1e-5, atol=1e-9))


def _rollout_arrays(rollout: LoadedRollout) -> list[np.ndarray]:
    arrays = [rollout.time_s, rollout.thorax_positions]
    for value in (rollout.orientations_wxyz, rollout.com_positions):
        if value is not None:
            arrays.append(value)
    arrays.extend(rollout.joint_positions.values())
    arrays.extend(rollout.joint_velocity.values())
    arrays.extend(rollout.joint_acceleration.values())
    arrays.extend(rollout.contacts.values())
    return [np.asarray(array, dtype=float) for array in arrays]


def _find_metric_files(dataset: Path, metrics_root: Path) -> list[Path]:
    candidates = [dataset / "metrics.json", dataset / "metrics" / "metrics.json", dataset / "analysis" / "metrics.json"]
    if metrics_root.is_dir():
        candidates.extend(path for path in metrics_root.rglob("*.json") if dataset.name in path.parts or path.stem == dataset.name)
    return sorted({path.resolve() for path in candidates if path.is_file()}, key=lambda item: item.as_posix())


def _manifest_files(manifest: Any) -> dict[str, str | None]:
    if not isinstance(manifest, Mapping):
        return {}
    result: dict[str, str | None] = {}
    files = manifest.get("files", manifest.get("entries", {}))
    if isinstance(files, Mapping):
        iterable = files.items()
    elif isinstance(files, list):
        iterable = ((item.get("path", item.get("name", "")), item) for item in files if isinstance(item, Mapping))
    else:
        iterable = ()
    for relative, value in iterable:
        if not relative:
            continue
        expected = value.get("sha256") if isinstance(value, Mapping) else value if isinstance(value, str) and len(value) == 64 else None
        result[str(relative)] = expected
    checksums = manifest.get("checksums")
    if isinstance(checksums, Mapping):
        for relative, value in checksums.items():
            result.setdefault(str(relative), str(value) if value else None)
    return result


def _read_checksum_file(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split(maxsplit=1)
        if len(parts) == 2 and len(parts[0]) == 64:
            result[parts[1].lstrip("* ")] = parts[0]
    return result


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _first_file(root: Path, names: Iterable[str]) -> Path | None:
    for name in names:
        path = root / name
        if path.is_file():
            return path
    return None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _flatten_scalars(value: Any, prefix: str = "") -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {prefix: value} if prefix else {}
    result: dict[str, Any] = {}
    for key, item in value.items():
        name = str(key)
        result[name] = item if not isinstance(item, Mapping) else item
        if isinstance(item, Mapping):
            nested = _flatten_scalars(item, f"{prefix}.{name}" if prefix else name)
            result.update(nested)
            for nested_name, nested_value in nested.items():
                result.setdefault(nested_name.rsplit(".", 1)[-1], nested_value)
    return result


def _numeric_values(value: Any) -> list[float]:
    if isinstance(value, (bool, np.bool_)):
        return []
    if isinstance(value, Mapping):
        result: list[float] = []
        for item in value.values():
            result.extend(_numeric_values(item))
        return result
    if isinstance(value, (list, tuple, np.ndarray)):
        result: list[float] = []
        for item in value:
            result.extend(_numeric_values(item))
        return result
    try:
        return [float(value)]
    except (TypeError, ValueError):
        return []


def _metadata_number(metadata: Mapping[str, Any], keys: Iterable[str]) -> float | None:
    for key in keys:
        value = metadata.get(key)
        numeric = _numeric_values(value)
        if numeric and np.isfinite(numeric[0]):
            return numeric[0]
    return None


def _integrity_row(dataset: Path, check: str, artifact: str, status: str, details: str = "") -> dict[str, Any]:
    return {"dataset_id": dataset.name, "check": check, "artifact": artifact, "status": status, "details": details}


def _empty_row(kind: str, status: str) -> dict[str, Any]:
    return {"dataset_id": "", "check": kind, "status": status, "details": "No dataset artifacts were discovered."}


def _cell(value: Any) -> str:
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True, default=str)
    return "" if value is None else str(value)


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows({key: _cell(row.get(key)) for key in keys} for row in rows)


def _warnings(dataset_rows: Sequence[Mapping[str, Any]], metric_rows: Sequence[Mapping[str, Any]], campaign: Mapping[str, Any], validation: Mapping[str, Any]) -> list[str]:
    warnings = []
    if any(row.get("status") == FAILED for row in dataset_rows):
        warnings.append("At least one dataset failed an integrity or consistency check.")
    if any(row.get("status") in {"MISSING_METRIC", "UNAVAILABLE_METRIC", "INVALID_METRIC"} for row in metric_rows):
        warnings.append("Some metrics are missing, unavailable, or invalid.")
    if campaign.get("status") == "MISSING_CAMPAIGN_DATA":
        warnings.append("campaign_data.json is not available.")
    if validation.get("status") != PASS:
        warnings.append("Validation readiness is incomplete; no biological interpretation is made.")
    return warnings


def _summary_markdown(summary: Mapping[str, Any]) -> str:
    datasets = summary["datasets"]
    runtime = summary["runtime"]
    calibration = summary["calibration"]
    validation = summary["validation"]
    warnings = summary["warnings"]
    lines = [
        "# Artifact Analysis Summary",
        "",
        f"**Status:** `{summary['status']}`",
        "",
        "This is a read-only computational artifact audit. It does not create data, validate biology, diagnose disease, predict clinical outcomes, or evaluate drug response.",
        "",
        "## Readiness",
        "",
        f"- Runtime: `{runtime['status']}`",
        f"- Datasets: `{datasets['count']}` discovered; `{datasets['valid_count']}` passed; `{datasets['failed_count']}` failed",
        f"- Campaign: `{summary['campaign']['status']}`",
        f"- Calibration: `{calibration['status']}`; possible = `{calibration['calibration_possible']}`",
        f"- Validation: `{validation['status']}`; holdout possible = `{validation['holdout_possible']}`",
        "",
        "## Warnings",
        "",
    ]
    lines.extend(f"- {warning}" for warning in warnings) if warnings else lines.append("- None recorded.")
    lines.extend(["", "## Output tables", "", *[f"- `{name}`" for name in OUTPUT_NAMES if name != "artifact_summary.md"], ""])
    return "\n".join(lines)
