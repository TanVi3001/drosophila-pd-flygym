"""Read-only validation tools for imported research datasets.

The commands in this module inspect artifacts that already exist.  They do
not run simulations, repair files, infer missing measurements, or make
biological interpretations.  A missing rollout is reported as
``WAITING_DATASET``.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


REQUIRED_ARTIFACTS = (
    "rollout.json",
    "manifest.json",
    "metadata.json",
    "viewer_pose.json",
    "metrics/metrics.json",
)
RECOMMENDED_ARTIFACTS = (
    "metrics/metrics.csv",
    "report/summary.md",
    "report/dashboard.html",
    "figures/",
)
REQUIRED_METRICS = (
    "walking_speed_mm_s",
    "total_distance_mm",
    "heading_variance_rad2",
    "body_orientation_variance_rad2",
    "symmetry_index",
    "trajectory_curvature_mean_rad_per_mm",
)
COMPARISON_METRICS = (
    "frame_count",
    "timestep_s",
    "duration_s",
    "walking_speed_mm_s",
    "walking_speed_max_mm_s",
    "total_distance_mm",
    "com_velocity_mean_mm_s",
    "heading_variance_rad2",
    "trajectory_curvature_mean_rad_per_mm",
)
BOUNDARY_TERMS = (
    "diagnosis",
    "clinical prediction",
    "clinical biomarker",
    "clinical value",
)


@dataclass(frozen=True)
class ValidationIssue:
    """One machine-readable validation finding."""

    code: str
    message: str
    severity: str = "error"
    path: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "path": self.path,
        }


def _json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return None, f"{type(error).__name__}: {error}"


def _mapping(value: Any) -> Mapping[str, Any] | None:
    return value if isinstance(value, Mapping) else None


def _rollout_data(payload: Any) -> Mapping[str, Any] | None:
    mapping = _mapping(payload)
    if mapping is None:
        return None
    nested = _mapping(mapping.get("rollout"))
    return nested if nested is not None else mapping


def _frames(payload: Any) -> list[Mapping[str, Any]]:
    data = _rollout_data(payload)
    values = data.get("frames") if data is not None else None
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        return []
    return [item for item in values if isinstance(item, Mapping)]


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if np.isfinite(result) else None


def _array(value: Any, *, width: int | None = None) -> np.ndarray | None:
    try:
        result = np.asarray(value, dtype=float)
    except (TypeError, ValueError):
        return None
    if result.size == 0 or not np.isfinite(result).all():
        return None
    if width is not None and (result.ndim != 1 or result.shape[0] != width):
        return None
    return result


def _frame_value(frame: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in frame:
            return frame[key]
    return None


def _timestamps(frames: Sequence[Mapping[str, Any]]) -> np.ndarray | None:
    values = []
    for frame in frames:
        value = _frame_value(frame, "timestamp_s", "timestamp", "time_s", "time")
        number = _number(value)
        if number is None:
            return None
        values.append(number)
    return np.asarray(values, dtype=float) if values else None


def _quaternions(frames: Sequence[Mapping[str, Any]]) -> tuple[int, list[int]]:
    checked = 0
    invalid: list[int] = []
    for index, frame in enumerate(frames):
        value = _frame_value(frame, "orientation", "quaternion", "thorax_orientation")
        if value is None:
            continue
        checked += 1
        quaternion = _array(value, width=4)
        if quaternion is None or float(np.linalg.norm(quaternion)) <= 0.0:
            invalid.append(index)
    return checked, invalid


def _com_values(frames: Sequence[Mapping[str, Any]]) -> tuple[int, list[int]]:
    checked = 0
    invalid: list[int] = []
    for index, frame in enumerate(frames):
        value = _frame_value(frame, "com", "COM", "center_of_mass")
        if value is None:
            continue
        checked += 1
        if _array(value, width=3) is None:
            invalid.append(index)
    return checked, invalid


def _metrics_value(metrics: Mapping[str, Any], name: str) -> Any:
    scalar = _mapping(metrics.get("scalar_metrics"))
    if scalar is not None and name in scalar:
        return scalar[name]
    return metrics.get(name)


def _npz_frame_count(path: Path) -> int | None:
    try:
        with np.load(path, allow_pickle=False) as archive:
            for key in ("thorax", "thorax_positions", "positions", "frames", "timestamp_s", "time_s"):
                if key in archive:
                    return int(len(archive[key]))
    except (OSError, ValueError, TypeError):
        return None
    return None


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_paths(root: Path) -> dict[str, Path]:
    result = {name: root / name for name in REQUIRED_ARTIFACTS}
    result["rollout.npz"] = root / "rollout.npz"
    result["rollout_arrays.npz"] = root / "rollout_arrays.npz"
    return result


def _report_markdown(title: str, payload: Mapping[str, Any]) -> str:
    lines = [f"# {title}", "", f"Generated: `{datetime.now(UTC).isoformat()}`", ""]
    status = payload.get("status", payload.get("overall_pass", "unknown"))
    lines.append(f"- Status: `{status}`")
    lines.append("- Scope: read-only computational artifact validation; no biological interpretation.")
    lines.append("")
    for section, value in payload.items():
        if section in {"status", "overall_pass", "generated_at", "scientific_scope"}:
            continue
        lines.extend([f"## {str(section).replace('_', ' ').title()}", ""])
        if isinstance(value, Mapping):
            for key, item in value.items():
                display = json.dumps(item, ensure_ascii=False, sort_keys=True) if isinstance(item, (dict, list)) else str(item)
                lines.append(f"- `{key}`: {display}")
        elif isinstance(value, list):
            lines.extend(f"- {item}" for item in value)
        else:
            lines.append(str(value))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _write_report(directory: str | Path, filename: str, title: str, payload: Mapping[str, Any]) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    (target / filename).write_text(_report_markdown(title, payload), encoding="utf-8")
    (target / filename.replace(".md", ".json")).write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return target / filename


def validate_dataset(
    dataset: str | Path,
    *,
    output: str | Path | None = None,
    write_report: bool = True,
) -> dict[str, Any]:
    """Validate one imported dataset without creating missing scientific data."""

    root = Path(dataset).expanduser().resolve()
    payload: dict[str, Any] = {
        "dataset": root.as_posix(),
        "dataset_id": root.name,
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "WAITING_DATASET",
        "overall_pass": False,
        "checks": {},
        "issues": [],
    }
    if not root.is_dir():
        payload["issues"] = [ValidationIssue("DATASET_MISSING", "Dataset directory does not exist.").as_dict()]
        if write_report and output is not None:
            _write_report(output, "validation_report.md", "Dataset Validation Report", payload)
        return payload

    paths = _artifact_paths(root)
    rollout_path = paths["rollout.json"]
    npz_path = next((paths[name] for name in ("rollout.npz", "rollout_arrays.npz") if paths[name].is_file()), None)
    if not rollout_path.is_file() and npz_path is None:
        payload["issues"] = [ValidationIssue("ROLLOUT_MISSING", "No rollout.json or rollout NPZ is available.").as_dict()]
        if write_report and output is not None:
            _write_report(output, "validation_report.md", "Dataset Validation Report", payload)
        return payload

    required_missing = [name for name in REQUIRED_ARTIFACTS if not paths[name].is_file()]
    required_missing = [name for name in required_missing if name != "rollout.json" or not rollout_path.is_file()]
    payload["checks"]["artifact_completeness"] = {
        "pass": not required_missing,
        "missing": required_missing,
        "npz_source": npz_path.name if npz_path else None,
        "recommended_missing": [name for name in RECOMMENDED_ARTIFACTS if not (root / name.rstrip("/")).exists()],
    }
    issues: list[ValidationIssue] = []
    if required_missing:
        issues.append(ValidationIssue("ARTIFACT_MISSING", f"Missing required artifacts: {', '.join(required_missing)}"))

    npz_count = _npz_frame_count(npz_path) if npz_path is not None else None
    payload["checks"]["rollout_npz"] = {
        "pass": npz_path is not None and npz_count is not None and npz_count > 0,
        "path": npz_path.name if npz_path else None,
        "frame_count": npz_count,
    }
    if not payload["checks"]["rollout_npz"]["pass"]:
        issues.append(ValidationIssue("ROLLOUT_NPZ_INVALID", "A rollout NPZ is missing, unreadable, or empty."))

    raw_rollout, rollout_error = _json(rollout_path) if rollout_path.is_file() else (None, None)
    frames = _frames(raw_rollout)
    if rollout_error:
        issues.append(ValidationIssue("ROLLOUT_JSON_INVALID", rollout_error, path=rollout_path.as_posix()))
    payload["checks"]["rollout_json"] = {
        "pass": rollout_path.is_file() and rollout_error is None and bool(frames),
        "frame_count": len(frames),
        "error": rollout_error,
    }

    raw_metadata, metadata_error = _json(paths["metadata.json"]) if paths["metadata.json"].is_file() else (None, None)
    metadata = _mapping(raw_metadata) or {}
    if metadata_error:
        issues.append(ValidationIssue("METADATA_INVALID", metadata_error, path=paths["metadata.json"].as_posix()))
    payload["checks"]["metadata"] = {"pass": paths["metadata.json"].is_file() and metadata_error is None, "error": metadata_error}

    raw_metrics, metrics_error = _json(paths["metrics/metrics.json"]) if paths["metrics/metrics.json"].is_file() else (None, None)
    metrics = _mapping(raw_metrics) or {}
    if metrics_error:
        issues.append(ValidationIssue("METRICS_INVALID", metrics_error, path=(root / "metrics/metrics.json").as_posix()))

    raw_pose, pose_error = _json(paths["viewer_pose.json"]) if paths["viewer_pose.json"].is_file() else (None, None)
    pose = _mapping(raw_pose) or {}
    if pose_error:
        issues.append(ValidationIssue("VIEWER_POSE_INVALID", pose_error, path=paths["viewer_pose.json"].as_posix()))
    pose_frames = _frames(raw_pose)
    pose_quaternion_count, pose_invalid_quaternions = _quaternions(pose_frames)
    payload["checks"]["viewer_pose"] = {
        "pass": paths["viewer_pose.json"].is_file() and pose_error is None and bool(pose_frames) and not pose_invalid_quaternions,
        "frame_count": len(pose_frames),
        "quaternion_checked": pose_quaternion_count,
        "invalid_quaternion_frames": pose_invalid_quaternions,
    }
    if pose_invalid_quaternions:
        issues.append(ValidationIssue("VIEWER_QUATERNION_INVALID", f"Viewer pose contains invalid quaternions at frames: {pose_invalid_quaternions}"))

    frame_sources = {"rollout.json": len(frames)} if frames else {}
    if npz_count is not None:
        frame_sources[npz_path.name] = npz_count
    if isinstance(pose.get("frames"), list):
        frame_sources["viewer_pose.json"] = len(pose["frames"])
    for name in ("frame_count",):
        value = _number(metrics.get(name))
        if value is not None:
            frame_sources["metrics.json"] = int(value)
    frame_values = list(frame_sources.values())
    frame_pass = bool(frame_values) and len(set(frame_values)) == 1 and frame_values[0] > 0
    payload["checks"]["frame_count"] = {"pass": frame_pass, "sources": frame_sources}
    if not frame_pass:
        issues.append(ValidationIssue("FRAME_COUNT_MISMATCH", "Frame counts are missing, empty, or inconsistent."))

    time_values = _timestamps(frames)
    timestep = _number(metadata.get("timestep_s", metadata.get("timestep")))
    if timestep is None:
        timestep = _number(metrics.get("timestep_s"))
    timestep_check: dict[str, Any] = {"pass": False, "available": time_values is not None, "declared_timestep_s": timestep}
    if time_values is not None and len(time_values) > 1:
        deltas = np.diff(time_values)
        strict = bool(np.all(deltas > 0))
        positive = timestep is not None and timestep > 0
        reconstructed = bool(metrics.get("timestamps_reconstructed", False))
        timestep_check.update({"strictly_increasing": strict, "observed_delta_s": float(np.median(deltas)), "reconstructed": reconstructed})
        timestep_check["pass"] = bool(strict and positive)
        if not strict and reconstructed:
            timestep_check["pass"] = True
            timestep_check["status"] = "warning: timestamps were reconstructed by the analysis/export path"
        if not timestep_check["pass"]:
            issues.append(ValidationIssue("TIMESTEP_INVALID", "Timestamps are not strictly increasing or timestep is unavailable."))
    elif len(frames) == 1:
        timestep_check.update({"pass": timestep is None or timestep > 0, "strictly_increasing": None})
    payload["checks"]["timestep"] = timestep_check

    quaternion_count, invalid_quaternions = _quaternions(frames)
    quaternion_check = {"pass": not invalid_quaternions, "available": quaternion_count > 0, "checked": quaternion_count, "invalid_frames": invalid_quaternions}
    payload["checks"]["quaternion"] = quaternion_check
    if invalid_quaternions:
        issues.append(ValidationIssue("QUATERNION_INVALID", f"Invalid or zero-norm quaternions at frames: {invalid_quaternions}"))

    com_count, invalid_com = _com_values(frames)
    payload["checks"]["com"] = {"pass": not invalid_com, "available": com_count > 0, "checked": com_count, "invalid_frames": invalid_com}
    if invalid_com:
        issues.append(ValidationIssue("COM_INVALID", f"COM values are invalid at frames: {invalid_com}"))

    missing_metrics = [name for name in REQUIRED_METRICS if _number(_metrics_value(metrics, name)) is None]
    payload["checks"]["metric_availability"] = {"pass": not missing_metrics, "missing": missing_metrics, "available_channels": metrics.get("available_channels", {})}
    if missing_metrics:
        issues.append(ValidationIssue("METRIC_UNAVAILABLE", f"Metrics unavailable: {', '.join(missing_metrics)}", severity="warning"))

    payload["issues"] = [item.as_dict() for item in issues]
    payload["status"] = "PASS" if not any(item.severity == "error" for item in issues) else "INVALID_DATASET"
    payload["overall_pass"] = payload["status"] == "PASS"
    if write_report:
        target = output if output is not None else root
        _write_report(target, "validation_report.md", "Dataset Validation Report", payload)
    return payload


def _dataset_summary(dataset: Path) -> dict[str, Any]:
    validation = validate_dataset(dataset, write_report=False)
    checks = validation.get("checks", {})
    sources = checks.get("frame_count", {}).get("sources", {})
    metrics_path = dataset / "metrics" / "metrics.json"
    metrics, _ = _json(metrics_path) if metrics_path.is_file() else (None, None)
    metric_map = _mapping(metrics) or {}
    return {
        "dataset": dataset.as_posix(),
        "dataset_id": dataset.name,
        "status": validation["status"],
        "frame_count": sources.get("rollout.json", sources.get("rollout.npz", sources.get("rollout_arrays.npz"))),
        "timestep_s": _number(metric_map.get("timestep_s")),
        "duration_s": _number(metric_map.get("duration_s")),
        "metrics": {name: _number(_metrics_value(metric_map, name)) for name in COMPARISON_METRICS if name not in {"frame_count", "timestep_s", "duration_s"}},
    }


def compare_rollouts(datasets: Sequence[str | Path], *, output: str | Path | None = None, tolerance: float = 1e-6) -> dict[str, Any]:
    """Compare available rollout statistics and report differences only."""

    roots = [Path(item).expanduser().resolve() for item in datasets]
    summaries = [_dataset_summary(root) for root in roots]
    rows = []
    for metric in COMPARISON_METRICS:
        values: dict[str, float | None] = {}
        for summary in summaries:
            if metric == "frame_count":
                value = summary["frame_count"]
            elif metric in {"timestep_s", "duration_s"}:
                value = summary[metric]
            else:
                value = summary["metrics"].get(metric)
            values[summary["dataset_id"]] = value
        numeric = [value for value in values.values() if value is not None]
        difference = False
        if numeric:
            baseline = numeric[0]
            difference = any(abs(value - baseline) > tolerance * max(1.0, abs(baseline)) for value in numeric[1:])
        rows.append({"metric": metric, "values": values, "difference": difference, "available_count": len(numeric)})
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "datasets": [summary["dataset_id"] for summary in summaries],
        "rows": rows,
        "differences": [row for row in rows if row["difference"]],
        "scientific_scope": "Statistical differences between imported runs only; no biological interpretation.",
    }
    if output is not None:
        _write_report(output, "cross_run_consistency.md", "Cross-run Consistency Report", payload)
    return payload


def _manifest_entries(root: Path, manifest: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    entries: dict[str, Mapping[str, Any]] = {}
    raw_entries = manifest.get("entries")
    if isinstance(raw_entries, Sequence) and not isinstance(raw_entries, (str, bytes)):
        for entry in raw_entries:
            mapping = _mapping(entry)
            if mapping:
                path = mapping.get("relative_path", mapping.get("path"))
                if path:
                    entries[str(path)] = mapping
    raw_files = _mapping(manifest.get("files"))
    if raw_files:
        for value in raw_files.values():
            mapping = _mapping(value)
            if mapping and mapping.get("path"):
                entries[str(mapping["path"])] = mapping
    checksums = _mapping(manifest.get("checksums"))
    if checksums:
        for path, checksum in checksums.items():
            current = dict(entries.get(str(path), {}))
            current.setdefault("sha256", checksum)
            entries[str(path)] = current
    return entries


def _safe_manifest_path(root: Path, relative: str) -> Path | None:
    """Resolve a manifest path only when it stays inside the dataset root."""

    candidate = Path(relative)
    if candidate.is_absolute():
        return None
    dataset_root = root.resolve()
    resolved = (dataset_root / candidate).resolve()
    try:
        resolved.relative_to(dataset_root)
    except ValueError:
        return None
    return resolved


def verify_artifact_integrity(dataset: str | Path, *, output: str | Path | None = None) -> dict[str, Any]:
    """Verify hashes and cross-file metadata consistency without repair."""

    root = Path(dataset).expanduser().resolve()
    payload: dict[str, Any] = {"dataset": root.as_posix(), "status": "WAITING_DATASET", "checks": {}, "issues": []}
    manifest_path = root / "manifest.json"
    manifest, manifest_error = _json(manifest_path) if manifest_path.is_file() else (None, None)
    if not root.is_dir() or not manifest_path.is_file():
        payload["issues"] = [ValidationIssue("MANIFEST_MISSING", "Dataset or manifest.json is not available.").as_dict()]
        if output is not None:
            _write_report(output, "integrity_report.md", "Artifact Integrity Report", payload)
        return payload
    manifest_map = _mapping(manifest) or {}
    if manifest_error or not manifest_map:
        payload["issues"] = [ValidationIssue("MANIFEST_INVALID", manifest_error or "manifest.json must contain an object.").as_dict()]
    entries = _manifest_entries(root, manifest_map)
    hash_results = []
    unsafe_paths: list[str] = []
    for relative, entry in sorted(entries.items()):
        path = _safe_manifest_path(root, relative)
        expected = entry.get("sha256")
        if path is None:
            unsafe_paths.append(relative)
            hash_results.append({"path": relative, "exists": False, "expected": expected, "observed": None, "pass": False, "error": "path escapes dataset root"})
            continue
        exists = path.is_file()
        observed = _file_hash(path) if exists else None
        hash_results.append({"path": relative, "exists": exists, "expected": expected, "observed": observed, "pass": exists and bool(expected) and observed == str(expected)})
    payload["checks"]["sha256"] = {"pass": bool(hash_results) and all(item["pass"] for item in hash_results), "files": hash_results}
    if not payload["checks"]["sha256"]["pass"]:
        payload["issues"].append(ValidationIssue("HASH_MISMATCH", "One or more manifest file hashes are missing, absent, or mismatched.").as_dict())
    if unsafe_paths:
        payload["issues"].append(ValidationIssue("MANIFEST_PATH_UNSAFE", "Manifest entries must remain inside the dataset root.", path=", ".join(unsafe_paths)).as_dict())

    validation = validate_dataset(root, write_report=False)
    manifest_count = _number(manifest_map.get("frame_count"))
    observed_count = validation["checks"].get("frame_count", {}).get("sources", {}).get("rollout.json")
    manifest_count_pass = manifest_count is None or observed_count is None or int(manifest_count) == int(observed_count)
    payload["checks"]["manifest_consistency"] = {
        "pass": validation["status"] != "INVALID_DATASET" and manifest_count_pass,
        "dataset_status": validation["status"],
        "manifest_frame_count": int(manifest_count) if manifest_count is not None else None,
        "observed_frame_count": observed_count,
    }
    if not manifest_count_pass:
        payload["issues"].append(ValidationIssue("MANIFEST_FRAME_COUNT_MISMATCH", "Manifest frame_count does not match rollout.json.").as_dict())

    identity_values: dict[str, str] = {}
    metadata_path = root / "metadata.json"
    metrics_path = root / "metrics" / "metrics.json"
    pose_path = root / "viewer_pose.json"
    for source, path in (("metadata.json", metadata_path), ("metrics.json", metrics_path), ("viewer_pose.json", pose_path)):
        document, error = _json(path) if path.is_file() else (None, None)
        mapping = _mapping(document) or {}
        value = mapping.get("dataset_id")
        if value is None and source == "metadata.json":
            value = mapping.get("id")
        if value is not None and error is None:
            identity_values[source] = str(value)
    identity_consistent = len(set(identity_values.values())) <= 1
    payload["checks"]["metadata_consistency"] = {"pass": identity_consistent, "dataset_ids": identity_values}
    if not identity_consistent:
        payload["issues"].append(ValidationIssue("METADATA_MISMATCH", "Dataset identifiers disagree across metadata artifacts.").as_dict())

    report_paths = (root / "report" / "summary.md", root / "report" / "dashboard.html")
    report_pass = all(path.is_file() and path.stat().st_size > 0 for path in report_paths)
    payload["checks"]["viewer_pose_consistency"] = {
        "pass": bool(validation["checks"].get("viewer_pose", {}).get("pass", False)),
        "source_check": "viewer_pose",
    }
    if not payload["checks"]["viewer_pose_consistency"]["pass"]:
        payload["issues"].append(ValidationIssue("VIEWER_POSE_MISMATCH", "Viewer pose is missing, malformed, or inconsistent with the rollout.").as_dict())
    payload["checks"]["report_consistency"] = {
        "pass": report_pass,
        "required": [path.relative_to(root).as_posix() for path in report_paths],
        "missing": [path.relative_to(root).as_posix() for path in report_paths if not path.is_file()],
    }
    if not report_pass:
        payload["issues"].append(ValidationIssue("REPORT_MISSING", "The expected report summary or dashboard is missing.").as_dict())
    payload["issues"].extend(item for item in validation["issues"] if item["severity"] == "error")
    payload["status"] = "PASS" if not payload["issues"] and payload["checks"]["sha256"]["pass"] else "INVALID_ARTIFACTS"
    payload["overall_pass"] = payload["status"] == "PASS"
    target = output if output is not None else root
    _write_report(target, "integrity_report.md", "Artifact Integrity Report", payload)
    return payload


def _is_negated(text: str, term: str) -> bool:
    """Recognize common disclaimer wording in a small document context."""

    lowered = text.casefold()
    pattern = (
        r"(?:\b(?:not|no|never|without|does not|do not|cannot|can't|outside|beyond)\b|không|khong)"
        r"[^.\n]{0,140}\b" + re.escape(term.casefold()) + r"\b"
    )
    return bool(re.search(pattern, lowered))


def check_scientific_boundaries(root: str | Path, *, output: str | Path | None = None) -> dict[str, Any]:
    """Scan Markdown documentation for unqualified clinical or biological claims."""

    base = Path(root).expanduser().resolve()
    findings: list[dict[str, Any]] = []
    for path in sorted(base.rglob("*.md")) if base.is_dir() else ():
        if any(part in {".git", ".pytest_cache", "__pycache__", ".venv", "venv"} for part in path.parts):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError):
            continue
        for number, line in enumerate(lines, start=1):
            lowered = line.casefold()
            for term in BOUNDARY_TERMS:
                if term in lowered:
                    context = " ".join(lines[max(0, number - 8):number])
                    findings.append({
                        "path": path.relative_to(base).as_posix(),
                        "line": number,
                        "term": term,
                        "classification": "boundary_disclaimer" if _is_negated(context, term) else "potential_overclaim",
                        "text": line.strip(),
                    })
    violations = [item for item in findings if item["classification"] == "potential_overclaim"]
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "PASS" if not violations else "REVIEW_REQUIRED",
        "scanned_root": base.as_posix(),
        "findings": findings,
        "violations": violations,
        "scientific_scope": "Text scan only; findings require human review and do not establish scientific validity.",
    }
    if output is not None:
        _write_report(output, "scientific_boundary_report.md", "Scientific Boundary Check", payload)
    return payload


def check_end_to_end_runtime(repository_root: str | Path = ".", *, execute: bool = False) -> dict[str, Any]:
    """Report runtime availability; execute only when explicitly requested."""

    root = Path(repository_root).expanduser().resolve()
    required = ("flygym", "mujoco", "flygym_demo")
    missing = [name for name in required if importlib.util.find_spec(name) is None]
    if missing:
        return {"status": "SKIPPED", "missing_dependencies": missing, "reason": "FlyGym runtime unavailable; no simulation was started."}
    if not execute:
        return {"status": "READY_NOT_EXECUTED", "missing_dependencies": [], "reason": "Runtime is available; pass --run-e2e to execute the existing demo pipeline."}
    script = root / "scripts" / "run_demo.py"
    completed = subprocess.run([sys.executable, str(script), "--no-install-simulation"], cwd=root, capture_output=True, text=True, check=False)
    return {"status": "PASS" if completed.returncode == 0 else "FAILED", "returncode": completed.returncode, "stdout": completed.stdout[-4000:], "stderr": completed.stderr[-4000:]}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, help="Dataset directory to validate")
    parser.add_argument("--compare", nargs="+", type=Path, help="Two or more dataset directories to compare")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root for the boundary scan")
    parser.add_argument("--output", type=Path, default=Path("results/validation"), help="Validation report directory")
    parser.add_argument("--skip-boundary", action="store_true")
    parser.add_argument("--run-e2e", action="store_true", help="Run existing run_demo.py only when FlyGym dependencies are present")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs: dict[str, Any] = {"end_to_end": check_end_to_end_runtime(args.root, execute=args.run_e2e)}
    if args.dataset is not None:
        outputs["dataset"] = validate_dataset(args.dataset, output=args.output)
        outputs["integrity"] = verify_artifact_integrity(args.dataset, output=args.output)
    if args.compare:
        outputs["cross_run"] = compare_rollouts(args.compare, output=args.output)
    if not args.skip_boundary:
        outputs["boundary"] = check_scientific_boundaries(args.root, output=args.output)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "research_validation.json").write_text(json.dumps(outputs, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(outputs, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
