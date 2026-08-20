"""Build signatures from existing JSON summaries only."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .signature import DiseaseSignature, SIGNATURE_FIELDS, UNAVAILABLE


_ALIASES = {
    "walking_speed": ("walking_speed", "walking_speed_mm_s", "mean_planar_speed_mm_s", "mean_walking_speed_mm_s"),
    "stride_length": ("stride_length", "stride_length_mm", "stride_length_mean", "mean_stride_length_mm"),
    "step_frequency": ("step_frequency", "step_frequency_hz", "stride_frequency_hz"),
    "pause_fraction": ("pause_fraction", "pause_ratio"),
    "heading_variance": ("heading_variance", "heading_variance_rad2"),
    "turning_rate": ("turning_rate", "turning_rate_rad_s"),
    "symmetry_index": ("symmetry_index", "symmetry_score"),
    "trajectory_efficiency": ("trajectory_efficiency", "locomotion_efficiency"),
    "orientation_stability": ("orientation_stability", "orientation_stability_score"),
    "joint_velocity_mean": ("joint_velocity_mean", "joint_rms_velocity", "joint_rms_velocity_mean"),
    "joint_velocity_std": ("joint_velocity_std", "joint_rms_velocity_std"),
    "com_displacement": ("com_displacement", "com_displacement_mm"),
    "path_length": ("path_length", "path_length_mm", "planar_path_length_mm", "total_distance_mm"),
}


def build_signature(
    *,
    metrics: Mapping[str, Any] | str | Path | None = None,
    biomarkers: Mapping[str, Any] | str | Path | None = None,
    rollout_summary: Mapping[str, Any] | str | Path | None = None,
    signature_id: str | None = None,
) -> DiseaseSignature:
    """Build a signature from summary documents without loading rollout frames."""

    documents: list[tuple[str, Mapping[str, Any], str]] = []
    for label, document in (("metrics", metrics), ("biomarkers", biomarkers), ("rollout_summary", rollout_summary)):
        if document is None:
            continue
        documents.append((label, _load_mapping(document), str(document) if isinstance(document, (str, Path)) else label))
    if not documents:
        raise ValueError("At least one metrics, biomarkers, or rollout_summary document is required.")

    flattened = [mapping for _, document, _ in documents for mapping in _candidate_mappings(document)]
    values = {
        field_name: _first_value(flattened, _ALIASES[field_name])
        for field_name in SIGNATURE_FIELDS
    }
    identifier = signature_id or _first_identifier(flattened)
    source = tuple(source_name for _, _, source_name in documents)
    metadata = {"source_documents": [label for label, _, _ in documents]}
    return DiseaseSignature.from_mapping(values, signature_id=identifier, source=source, metadata=metadata)


def build_signature_from_files(
    metrics_path: str | Path | None = None,
    biomarkers_path: str | Path | None = None,
    rollout_summary_path: str | Path | None = None,
    *,
    signature_id: str | None = None,
) -> DiseaseSignature:
    """File-oriented builder used by scripts and notebooks."""

    return build_signature(
        metrics=metrics_path,
        biomarkers=biomarkers_path,
        rollout_summary=rollout_summary_path,
        signature_id=signature_id,
    )


def build_signature_from_directory(dataset_dir: str | Path, *, signature_id: str | None = None) -> DiseaseSignature:
    """Discover existing summary JSON files under one dataset directory."""

    root = Path(dataset_dir).expanduser()
    if not root.is_dir():
        raise FileNotFoundError(f"Dataset directory not found: {root}")
    metrics_path = _first_file(root, ("metrics/metrics.json", "metrics.json"))
    biomarkers_path = _first_file(root, ("biomarkers/biomarkers.json", "biomarkers.json"))
    summary_path = _first_file(root, ("rollout_summary.json", "report/rollout_summary.json", "summary.json"))
    if not any((metrics_path, biomarkers_path, summary_path)):
        raise FileNotFoundError(f"No supported signature summary found under {root}")
    return build_signature_from_files(
        metrics_path,
        biomarkers_path,
        summary_path,
        signature_id=signature_id or root.name,
    )


def load_signature(path: str | Path) -> DiseaseSignature:
    """Load a standalone signature JSON or discover summaries in a directory."""

    source = Path(path).expanduser()
    if source.is_dir():
        return build_signature_from_directory(source)
    if not source.is_file():
        raise FileNotFoundError(f"Signature input not found: {source}")
    payload = _read_json(source)
    if isinstance(payload.get("values"), Mapping):
        return DiseaseSignature.from_mapping(payload, signature_id=payload.get("signature_id"), source=(str(source),))
    if source.name == "metrics.json":
        return build_signature(metrics=payload, signature_id=payload.get("dataset_id"))
    if source.name == "biomarkers.json":
        return build_signature(biomarkers=payload, signature_id=payload.get("dataset_id"))
    return build_signature(rollout_summary=payload, signature_id=payload.get("dataset_id"))


def _load_mapping(document: Mapping[str, Any] | str | Path) -> Mapping[str, Any]:
    if isinstance(document, Mapping):
        return document
    return _read_json(Path(document))


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {path}: {error}") from error
    if not isinstance(payload, Mapping):
        raise ValueError(f"JSON document must contain an object: {path}")
    return dict(payload)


def _candidate_mappings(document: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    candidates: list[Mapping[str, Any]] = [document]
    for key in ("scalar_metrics", "derived_locomotion_metrics", "metrics", "values"):
        value = document.get(key)
        if isinstance(value, Mapping):
            candidates.append(value)
    biomarkers = document.get("biomarkers")
    if isinstance(biomarkers, Mapping):
        extracted: dict[str, Any] = {}
        for name, value in biomarkers.items():
            if isinstance(value, Mapping) and "value" in value:
                extracted[name] = value["value"]
            else:
                extracted[name] = value
        candidates.append(extracted)
    return tuple(candidates)


def _first_value(mappings: list[Mapping[str, Any]], aliases: tuple[str, ...]) -> Any:
    for mapping in mappings:
        for alias in aliases:
            value = mapping.get(alias)
            if value not in (None, "", UNAVAILABLE):
                return value
    return UNAVAILABLE


def _first_identifier(mappings: list[Mapping[str, Any]]) -> str | None:
    for mapping in mappings:
        for key in ("signature_id", "dataset_id", "condition_id", "experiment_id"):
            value = mapping.get(key)
            if value not in (None, ""):
                return str(value)
    return None


def _first_file(root: Path, relative_paths: tuple[str, ...]) -> Path | None:
    for relative_path in relative_paths:
        candidate = root / relative_path
        if candidate.is_file():
            return candidate
    return None


__all__ = ["build_signature", "build_signature_from_directory", "build_signature_from_files", "load_signature"]
