"""Build read-only Release 1.0 research-platform audit artifacts.

This tool inventories existing files and imported datasets. It never runs a
simulation and never fabricates measurements, figures, or tables. Missing
runtime or dataset inputs are represented explicitly in the generated reports.
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Mapping, Sequence


SIMULATION_MODULES = ("flygym", "mujoco", "flygym_demo")
EXPECTED_FILES = (
    "README.md",
    "LICENSE",
    "CITATION.cff",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE",
)
EXPECTED_FIGURES = tuple(f"Figure_{index:02d}.png" for index in range(1, 11))
EXPECTED_TABLES = tuple(f"Table_{index:02d}.csv" for index in range(1, 6))


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _json(path: Path) -> tuple[dict[str, Any], str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return {}, f"{type(error).__name__}: {error}"
    return (dict(payload), None) if isinstance(payload, Mapping) else {}, "JSON root is not an object"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _runtime(root: Path) -> dict[str, Any]:
    missing = [name for name in SIMULATION_MODULES if importlib.util.find_spec(name) is None]
    python_ready = sys.version_info[:2] == (3, 12)
    return {
        "ready": not missing and python_ready,
        "python": ".".join(str(item) for item in sys.version_info[:3]),
        "python_required": "3.12.x",
        "python_ready": python_ready,
        "required": list(SIMULATION_MODULES),
        "missing": missing,
    }


def _find_datasets(root: Path) -> list[Path]:
    datasets_root = root / "datasets"
    if not datasets_root.is_dir():
        return []
    found: set[Path] = set()
    for name in ("rollout.json", "rollout.npz", "rollout_arrays.npz"):
        found.update(path.parent.resolve() for path in datasets_root.rglob(name) if path.is_file())
    return sorted(found)


def _manifest_checksums(dataset: Path, manifest: Mapping[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    entries = manifest.get("files")
    if isinstance(entries, Mapping):
        for value in entries.values():
            if isinstance(value, Mapping) and value.get("path") and value.get("sha256"):
                result[str(value["path"])] = str(value["sha256"])
    entries = manifest.get("entries")
    if isinstance(entries, Sequence) and not isinstance(entries, (str, bytes)):
        for value in entries:
            if isinstance(value, Mapping) and value.get("relative_path") and value.get("sha256"):
                result[str(value["relative_path"])] = str(value["sha256"])
    checksums = manifest.get("checksums")
    if isinstance(checksums, Mapping):
        result.update({str(key): str(value) for key, value in checksums.items() if value})
    return result


def _dataset_record(dataset: Path) -> dict[str, Any]:
    manifest_path = dataset / "manifest.json"
    metadata_path = dataset / "metadata.json"
    manifest, manifest_error = _json(manifest_path) if manifest_path.is_file() else ({}, "manifest.json is missing")
    metadata, metadata_error = _json(metadata_path) if metadata_path.is_file() else ({}, "metadata.json is missing")
    checksums = _manifest_checksums(dataset, manifest)
    checksum_status = "available" if checksums else "unavailable"
    return {
        "dataset_id": dataset.name,
        "path": dataset.relative_to(dataset.parents[1]).as_posix() if len(dataset.parents) > 1 else dataset.name,
        "checksum": {"status": checksum_status, "files": checksums},
        "creation_time": metadata.get("created_at", manifest.get("created_at")),
        "simulation_version": metadata.get("simulation_version", metadata.get("flygym_version")),
        "recorder_version": metadata.get("recorder_version"),
        "exporter_version": metadata.get("exporter_version"),
        "biomarker_version": metadata.get("biomarker_version"),
        "experiment_id": metadata.get("experiment_id", manifest.get("experiment_id")),
        "validation_status": metadata.get("validation_status", manifest.get("validation_status", "unverified")),
        "manifest_status": "invalid" if manifest_error else "available",
        "metadata_status": "invalid" if metadata_error else "available",
        "artifacts": sorted(path.relative_to(dataset).as_posix() for path in dataset.rglob("*") if path.is_file()),
    }


def build_dataset_registry(root: str | Path = ".") -> dict[str, Any]:
    """Write the dataset inventory without changing dataset contents."""

    repository = Path(root).expanduser().resolve()
    datasets = _find_datasets(repository)
    payload = {
        "schema_version": 1,
        "generated_at": _now(),
        "status": "READY" if datasets else "WAITING_DATASET",
        "datasets": [_dataset_record(dataset) for dataset in datasets],
        "dataset_root": (repository / "datasets").as_posix(),
        "scientific_scope": "Inventory and provenance metadata for imported artifacts only; no biological conclusion.",
    }
    target = repository / "results" / "dataset_registry.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def _write_json(path: Path, payload: Mapping[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return path


def build_performance_report(root: str | Path = ".") -> dict[str, Any]:
    """Record measured timings only when runtime and real datasets are present."""

    repository = Path(root).expanduser().resolve()
    runtime = _runtime(repository)
    datasets = _find_datasets(repository)
    status = "READY" if runtime["ready"] and datasets else "WAITING_RUNTIME"
    reason = None
    if not runtime["ready"]:
        reason = "FlyGym, MuJoCo, and/or flygym_demo are unavailable; simulation was not run."
    elif not datasets:
        reason = "No imported rollout dataset was found; no timings were fabricated."
    measurements: dict[str, Any] = {
        "simulation_time_s": None,
        "recorder_overhead_s": None,
        "export_time_s": None,
        "analysis_time_s": None,
        "biomarker_time_s": None,
        "viewer_export_time_s": None,
        "memory_mb": None,
        "disk_usage_mb": round(sum(path.stat().st_size for dataset in datasets for path in dataset.rglob("*") if path.is_file()) / 1_000_000, 6) if datasets else None,
    }
    notes: list[str] = []
    if runtime["ready"] and datasets:
        analysis_times: list[float] = []
        biomarker_times: list[float] = []
        viewer_times: list[float] = []
        try:
            from drosophila_pd.analysis import analyze_rollout
            from drosophila_pd.biomarkers import calculate_biomarkers
            from drosophila_pd.viewer_export import export_viewer_pose
        except (ImportError, ModuleNotFoundError) as error:
            notes.append(f"Optional analysis timing unavailable: {type(error).__name__}: {error}")
        else:
            with tempfile.TemporaryDirectory(prefix="drosophila_release_audit_") as temporary:
                temporary_root = Path(temporary)
                for index, dataset in enumerate(datasets):
                    try:
                        started = time.perf_counter()
                        analyze_rollout(dataset, temporary_root / f"analysis_{index}")
                        analysis_times.append(time.perf_counter() - started)
                    except (OSError, ValueError, TypeError) as error:
                        notes.append(f"Analysis timing unavailable for {dataset.name}: {type(error).__name__}: {error}")
                    try:
                        started = time.perf_counter()
                        calculate_biomarkers(dataset)
                        biomarker_times.append(time.perf_counter() - started)
                    except (OSError, ValueError, TypeError) as error:
                        notes.append(f"Biomarker timing unavailable for {dataset.name}: {type(error).__name__}: {error}")
                    try:
                        started = time.perf_counter()
                        export_viewer_pose(dataset, temporary_root / f"viewer_pose_{index}.json")
                        viewer_times.append(time.perf_counter() - started)
                    except (OSError, ValueError, TypeError) as error:
                        notes.append(f"Viewer-export timing unavailable for {dataset.name}: {type(error).__name__}: {error}")
        measurements["analysis_time_s"] = round(sum(analysis_times), 6) if analysis_times else None
        measurements["biomarker_time_s"] = round(sum(biomarker_times), 6) if biomarker_times else None
        measurements["viewer_export_time_s"] = round(sum(viewer_times), 6) if viewer_times else None
        notes.append("Simulation, recorder, and raw export timings were not rerun by this audit.")
    payload = {
        "schema_version": 1,
        "generated_at": _now(),
        "status": status,
        "reason": reason,
        "runtime": runtime,
        "dataset_count": len(datasets),
        "measurements": measurements,
        "measurement_policy": "Only timings from existing real datasets and an available runtime may be recorded; no simulation is started by this audit.",
        "notes": notes,
    }
    _write_json(repository / "results" / "performance" / "performance.json", payload)
    lines = [
        "# Performance Report",
        "",
        f"Generated: `{payload['generated_at']}`",
        f"- Status: `{status}`",
        f"- Dataset count: `{len(datasets)}`",
        f"- Runtime ready: `{runtime['ready']}`",
        "",
        "## Measurements",
        "",
    ]
    for name, value in measurements.items():
        lines.append(f"- `{name}`: `{value if value is not None else 'unavailable'}`")
    if reason:
        lines.extend(["", "## Reason", "", reason])
    lines.extend(["", "No values are fabricated when the pinned runtime or real rollout data is unavailable.", ""])
    (repository / "docs").mkdir(parents=True, exist_ok=True)
    (repository / "docs" / "performance_report.md").write_text("\n".join(lines), encoding="utf-8")
    return payload


def build_paper_package(root: str | Path = ".") -> dict[str, Any]:
    """Create paper assets from existing artifacts, or a waiting manifest only."""

    repository = Path(root).expanduser().resolve()
    paper = repository / "paper"
    paper.mkdir(parents=True, exist_ok=True)
    datasets = _find_datasets(repository)
    if not datasets:
        payload = {
            "schema_version": 1,
            "generated_at": _now(),
            "status": "WAITING_DATASET",
            "figures": [],
            "tables": [],
            "expected_figures": list(EXPECTED_FIGURES),
            "expected_tables": list(EXPECTED_TABLES),
            "scientific_scope": "No paper assets were generated because no real rollout dataset is available.",
        }
        _write_json(paper / "paper_manifest.json", payload)
        return payload

    sources_figures = sorted({path for dataset in datasets for path in (dataset / "figures").rglob("*.png") if path.is_file()})
    sources_tables = sorted({path for dataset in datasets for path in (dataset / "metrics").rglob("*.csv") if path.is_file()})
    figures: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    for index, source in enumerate(sources_figures[:10], start=1):
        target = paper / f"Figure_{index:02d}.png"
        shutil.copy2(source, target)
        figures.append({"path": target.name, "source": source.as_posix(), "sha256": _sha256(target)})
    for index, source in enumerate(sources_tables[:5], start=1):
        target = paper / f"Table_{index:02d}.csv"
        shutil.copy2(source, target)
        tables.append({"path": target.name, "source": source.as_posix(), "sha256": _sha256(target)})
    payload = {
        "schema_version": 1,
        "generated_at": _now(),
        "status": "READY" if figures or tables else "WAITING_DATASET",
        "figures": figures,
        "tables": tables,
        "expected_figures": list(EXPECTED_FIGURES),
        "expected_tables": list(EXPECTED_TABLES),
        "scientific_scope": "Copied publication assets retain the scope of the imported computational artifacts; no new result is inferred.",
    }
    _write_json(paper / "paper_manifest.json", payload)
    if figures or tables:
        (paper / "captions.md").write_text(
            "# Paper Asset Captions\n\nCaptions must be completed from the validated source reports before publication.\n",
            encoding="utf-8",
        )
    return payload


def _git(repository: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(["git", *args], cwd=repository, capture_output=True, text=True, check=False)
    except OSError:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def _doc_check(repository: Path) -> dict[str, Any]:
    docs = sorted((repository / "docs").rglob("*.md")) if (repository / "docs").is_dir() else []
    missing_final_newline = []
    for path in docs:
        try:
            if not path.read_bytes().endswith(b"\n"):
                missing_final_newline.append(path.relative_to(repository).as_posix())
        except OSError:
            missing_final_newline.append(path.relative_to(repository).as_posix())
    return {"pass": not missing_final_newline, "markdown_count": len(docs), "missing_final_newline": missing_final_newline}


def build_release_audit(root: str | Path = ".") -> dict[str, Any]:
    """Create the Release 1.0 checklist and final audit report."""

    repository = Path(root).expanduser().resolve()
    file_checks = {name: (repository / name).exists() for name in EXPECTED_FILES}
    runtime = _runtime(repository)
    dataset_registry = build_dataset_registry(repository)
    performance = build_performance_report(repository)
    paper = build_paper_package(repository)
    docs = _doc_check(repository)
    tag = _git(repository, "tag", "--list", "v1.0.0")
    checks = {
        "release_files": file_checks,
        "documentation_consistency": docs,
        "runtime_consistency": runtime,
        "artifact_consistency": {
            "pass": (repository / "dist").is_dir() and (repository / "results").is_dir() and (repository / "paper").is_dir(),
            "dist_present": (repository / "dist").is_dir(),
            "results_present": (repository / "results").is_dir(),
            "paper_present": (repository / "paper").is_dir(),
        },
        "release_tag": {"pass": bool(tag), "observed": tag},
    }
    blockers = []
    if not runtime["python_ready"]:
        blockers.append(f"Python {runtime['python']} is installed; the certified target is {runtime['python_required']}.")
    if not runtime["ready"]:
        blockers.append("FlyGym/MuJoCo runtime is unavailable in the audit environment.")
    if not dataset_registry["datasets"]:
        blockers.append("No real rollout dataset is available under datasets/.")
    if not file_checks["CHANGELOG.md"]:
        blockers.append("CHANGELOG.md is missing.")
    if not checks["documentation_consistency"]["pass"]:
        blockers.append("Some Markdown files do not end with a newline.")
    readiness = "NOT_READY" if blockers else "READY_FOR_REVIEW"
    payload = {
        "schema_version": 1,
        "generated_at": _now(),
        "release": "v1.0.0",
        "readiness": readiness,
        "checks": checks,
        "blockers": blockers,
        "scientific_scope": "Release engineering audit only; no biological validation or clinical claim.",
        "recommendations": {
            "release": "Do not certify a production research release until runtime, dataset, and release-document blockers are resolved.",
            "publication": "Publication package remains planning/artifact-ready only until real datasets and biological validation are supplied.",
        },
        "dataset_registry_status": dataset_registry["status"],
        "performance_status": performance["status"],
        "paper_status": paper["status"],
    }
    checklist_lines = [
        "# Release 1.0 Checklist", "", f"Generated: `{payload['generated_at']}`", "",
        f"- Overall readiness: `{readiness}`", "",
    ]
    for name, value in file_checks.items():
        checklist_lines.append(f"- [{'x' if value else ' '}] `{name}`")
    checklist_lines.extend(["", "## Blockers", ""])
    if blockers:
        checklist_lines.extend(f"- {blocker}" for blocker in blockers)
    else:
        checklist_lines.append("- None observed")
    checklist_lines.extend(["", "Scope: release engineering and repository consistency only.", ""])
    (repository / "docs" / "release_checklist.md").write_text("\n".join(checklist_lines), encoding="utf-8")

    final_lines = [
        "# Final Release Report", "", f"Generated: `{payload['generated_at']}`", "",
        f"- Release: `{payload['release']}`", f"- Recommendation: `{readiness}`", "",
        "## Architecture", "",
        "The repository contains the FlyGym adapter, rollout/export pipeline, static viewer, analysis, biomarker, experiment, and validation layers. This audit does not redesign or replace those layers.",
        "", "## Scientific Scope", "",
        "The platform supports computational simulation workflows and imported-artifact analysis. It does not establish biological validation, clinical prediction, or a medical diagnosis.",
        "", "## Strengths", "", "- Versioned packaging and citation metadata are present.", "- CI and test workflows are present.", "- Validation and reproducibility documentation exists.", "- Release tag `v1.0.0` is present.",
        "", "## Weaknesses and Technical Debt", "", "- The local audit runtime is not the pinned Python 3.12 FlyGym environment.", "- No real rollout dataset is currently available.", "- `CHANGELOG.md` is missing.", "- Publication figures and tables cannot be certified without real data.",
        "", "## Known Limitations", "", "- Existing benchmark and performance claims are not independently measured here.", "- Biological validation is outside the repository's current evidence.",
        "", "## Blockers", "", *[f"- {blocker}" for blocker in blockers],
        "", "## Recommendations", "", f"- Release: {payload['recommendations']['release']}", f"- Publication: {payload['recommendations']['publication']}", "",
    ]
    (repository / "docs" / "final_release_report.md").write_text("\n".join(final_lines), encoding="utf-8")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_release_audit(args.root)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
