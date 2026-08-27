"""Audit an externally supplied research-artifact archive without running simulation.

The tool inventories archive members, hashes them, parses JSON reports, and
records provenance gaps. It deliberately does not decode videos, import data
into the scientific pipeline, or infer biological meaning from filenames.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Iterable, Mapping
from zipfile import ZipFile


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VIDEO_SUFFIXES = {".avi", ".mkv", ".mov", ".mp4", ".webm"}
JSON_SUFFIXES = {".json"}
EXTERNAL_REFERENCE_MARKERS = (
    "bridge_scales",
    "brain_body_bridge",
    "fly-brain",
)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalized_member_name(name: str) -> str:
    return name.replace("\\", "/")


def _is_safe_member(name: str) -> bool:
    normalized = _normalized_member_name(name)
    path = PurePosixPath(normalized)
    windows_path = PureWindowsPath(normalized)
    return (
        not path.is_absolute()
        and not windows_path.is_absolute()
        and not windows_path.drive
        and ".." not in path.parts
    )


def _member_kind(name: str, is_directory: bool) -> str:
    if is_directory:
        return "directory"
    suffix = Path(_normalized_member_name(name)).suffix.lower()
    if suffix in VIDEO_SUFFIXES:
        return "video"
    if suffix in JSON_SUFFIXES:
        return "json"
    return "other"


def _nested_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for child in value.values():
            yield from _nested_values(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from _nested_values(child)


def _first_scalar(mapping: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
    return None


def _report_details(payload: Mapping[str, Any]) -> dict[str, Any]:
    baseline = payload.get("baseline")
    perturbed = payload.get("perturbed")
    baseline = baseline if isinstance(baseline, Mapping) else {}
    perturbed = perturbed if isinstance(perturbed, Mapping) else {}

    def metric_value(section: Mapping[str, Any], key: str) -> Any:
        metrics = section.get("derived_locomotion_metrics")
        return metrics.get(key) if isinstance(metrics, Mapping) else None

    values = {
        "baseline_sample_count": metric_value(baseline, "sample_count"),
        "perturbed_sample_count": metric_value(perturbed, "sample_count"),
        "baseline_step_count": metric_value(baseline, "step_count"),
        "perturbed_step_count": metric_value(perturbed, "step_count"),
        "baseline_timestep_s": metric_value(baseline, "timestep_s"),
        "perturbed_timestep_s": metric_value(perturbed, "timestep_s"),
        "baseline_speed_mm_s": metric_value(baseline, "mean_planar_speed_mm_s"),
        "perturbed_speed_mm_s": metric_value(perturbed, "mean_planar_speed_mm_s"),
    }
    source_strings = sorted(
        {
            text
            for text in _nested_values(payload)
            if any(marker in text for marker in EXTERNAL_REFERENCE_MARKERS)
        }
    )
    scopes = sorted(
        {
            text
            for section in (baseline, perturbed)
            for text in [section.get("scientific_scope")]
            if isinstance(text, str) and text
        }
    )
    environment = baseline.get("environment")
    environment = environment if isinstance(environment, Mapping) else {}
    configuration = baseline.get("configuration")
    configuration = configuration if isinstance(configuration, Mapping) else {}
    perturbation = payload.get("perturbation")
    perturbation = perturbation if isinstance(perturbation, Mapping) else {}
    expected_keys = {
        "experiment_id",
        "model",
        "perturbation",
        "baseline",
        "perturbed",
        "comparison",
        "overall_pass",
    }
    return {
        "document_type": "comparison_report" if expected_keys.issubset(payload) else "json_document",
        "experiment_id": _first_scalar(payload, "experiment_id"),
        "model": _first_scalar(payload, "model"),
        "overall_pass": _first_scalar(payload, "overall_pass"),
        "random_seed": _first_scalar(configuration, "random_seed", "seed"),
        "git_commit": baseline.get("git_commit"),
        "flygym_version": environment.get("flygym_version"),
        "mujoco_version": environment.get("mujoco_version"),
        "perturbation_parameters": perturbation.get("parameters", {}),
        "metrics": values,
        "scientific_scope": scopes,
        "external_source_references": source_strings,
    }


def _unresolved_references(
    members: list[dict[str, Any]],
    *,
    repo_root: Path,
) -> list[str]:
    references = sorted(
        {
            reference
            for member in members
            for reference in member.get("json_details", {}).get("external_source_references", [])
        }
    )
    unresolved: list[str] = []
    for reference in references:
        if "bridge_scales" in reference and not (repo_root / "data" / "bridge_scales").is_dir():
            unresolved.append(reference)
        elif "brain_body_bridge" in reference and not any(
            repo_root.rglob("brain_body_bridge.py")
        ):
            unresolved.append(reference)
        elif "fly-brain" in reference:
            unresolved.append(reference)
    return unresolved


def audit_archive(
    archive_path: str | Path,
    *,
    repo_root: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Audit ``archive_path`` and optionally write a JSON/Markdown report.

    The returned report is independent of the archive extraction location. No
    archive member is extracted by this function.
    """

    archive = Path(archive_path).expanduser().resolve()
    if not archive.is_file():
        raise FileNotFoundError(f"Archive not found: {archive}")
    root = Path(repo_root or REPOSITORY_ROOT).expanduser().resolve()

    members: list[dict[str, Any]] = []
    parse_errors: list[str] = []
    unsafe_members: list[str] = []
    with ZipFile(archive) as handle:
        infos = handle.infolist()
        name_counts = Counter(info.filename for info in infos)
        for info in infos:
            name = info.filename
            kind = _member_kind(name, info.is_dir())
            safe = _is_safe_member(name)
            row: dict[str, Any] = {
                "name": _normalized_member_name(name),
                "kind": kind,
                "size_bytes": int(info.file_size),
                "safe_path": safe,
                "duplicate_name": name_counts[name] > 1,
            }
            if not safe:
                unsafe_members.append(name)
                row["status"] = "UNSAFE_PATH"
                members.append(row)
                continue
            if info.is_dir():
                row["sha256"] = None
                row["status"] = "PRESENT"
                members.append(row)
                continue
            content = handle.read(info)
            row["sha256"] = _sha256_bytes(content)
            row["status"] = "PRESENT"
            if kind == "json":
                try:
                    payload = json.loads(content.decode("utf-8"))
                    if not isinstance(payload, Mapping):
                        raise ValueError("JSON root is not an object")
                    row["json_details"] = _report_details(payload)
                    row["status"] = "PARSED"
                except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                    row["status"] = "INVALID_JSON"
                    row["error"] = f"{type(exc).__name__}: {exc}"
                    parse_errors.append(name)
            elif kind == "video":
                row["status"] = "PRESENT_NOT_DECODED"
            members.append(row)

    json_members = [member for member in members if member["kind"] == "json"]
    video_members = [member for member in members if member["kind"] == "video"]
    unresolved = _unresolved_references(members, repo_root=root)
    duplicate_names = sorted(name for name, count in name_counts.items() if count > 1)
    raw_rollout_members = [
        member["name"]
        for member in members
        if Path(member["name"]).name.lower() in {"rollout.json", "rollout.npz", "rollout_arrays.npz"}
    ]
    viewer_pose_members = [
        member["name"] for member in members if Path(member["name"]).name.lower() == "viewer_pose.json"
    ]
    status = "PARSEABLE_DERIVED_ARTIFACTS"
    if unsafe_members or duplicate_names or parse_errors:
        status = "INVALID_ARCHIVE"

    report: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "archive": {
            "name": archive.name,
            "size_bytes": archive.stat().st_size,
            "sha256": _sha256_file(archive),
        },
        "status": status,
        "inventory": {
            "member_count": len(members),
            "json_count": len(json_members),
            "video_count": len(video_members),
            "other_count": sum(member["kind"] == "other" for member in members),
            "duplicate_names": duplicate_names,
            "unsafe_members": sorted(unsafe_members),
            "invalid_json_members": sorted(parse_errors),
            "raw_rollout_members": raw_rollout_members,
            "viewer_pose_members": viewer_pose_members,
        },
        "json_reports": [
            {
                "name": member["name"],
                "sha256": member["sha256"],
                "status": member["status"],
                **member.get("json_details", {}),
                **({"error": member["error"]} if "error" in member else {}),
            }
            for member in json_members
        ],
        "provenance": {
            "unresolved_external_references": unresolved,
            "video_decode": "NOT_PERFORMED",
            "raw_rollout_present": bool(raw_rollout_members),
            "viewer_pose_present": bool(viewer_pose_members),
            "interpretation": (
                "Archive is treated as derived computational output until the "
                "source repository, raw rollouts, runtime manifest, and video "
                "provenance are supplied."
            ),
        },
        "scientific_scope": (
            "This is an artifact and provenance audit only. It does not validate "
            "biological Parkinson phenotypes, clinical claims, or video content."
        ),
        "members": members,
    }
    if output_dir is not None:
        output = Path(output_dir).expanduser()
        if not output.is_absolute():
            output = root / output
        _write_report(report, output.resolve())
    return report


def _write_report(report: Mapping[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "audit.md").write_text(_markdown_report(report), encoding="utf-8")


def _markdown_report(report: Mapping[str, Any]) -> str:
    archive = report["archive"]
    inventory = report["inventory"]
    provenance = report["provenance"]
    lines = [
        "# External Artifact Audit",
        "",
        f"- Archive: `{archive['name']}`",
        f"- SHA256: `{archive['sha256']}`",
        f"- Status: **{report['status']}**",
        "",
        "## Inventory",
        "",
        f"- Members: {inventory['member_count']}",
        f"- JSON: {inventory['json_count']}",
        f"- Video: {inventory['video_count']}",
        f"- Other: {inventory['other_count']}",
        f"- Raw rollout files: {len(inventory['raw_rollout_members'])}",
        f"- Viewer pose files: {len(inventory['viewer_pose_members'])}",
        "",
        "## JSON Reports",
        "",
        "| File | Model | Status | Overall pass | Samples | Speed (baseline -> perturbed) |",
        "| --- | --- | --- | --- | ---: | ---: |",
    ]
    for item in report["json_reports"]:
        metrics = item.get("metrics", {})
        lines.append(
            "| `{name}` | `{model}` | {status} | {passed} | {samples} | {base} -> {perturbed} |".format(
                name=item["name"],
                model=item.get("model") or "",
                status=item["status"],
                passed=item.get("overall_pass", ""),
                samples=metrics.get("baseline_sample_count", ""),
                base=metrics.get("baseline_speed_mm_s", ""),
                perturbed=metrics.get("perturbed_speed_mm_s", ""),
            )
        )
    lines.extend(
        [
            "",
            "## Provenance and Scope",
            "",
            "- Video bytes were inventoried and hashed but not decoded by this tool.",
            "- The archive contains derived reports and videos, not `rollout.json`, `rollout.npz`, or `viewer_pose.json`.",
            "- JSON fields referencing an external `bridge_scales`/`fly-brain` source are unresolved against this repository.",
            "- The reports do not provide a source git commit (`git_commit` is null); reproducibility is therefore incomplete.",
            "- The files must not be presented as raw biological recordings or as biological validation.",
            "",
            "### Unresolved references",
            "",
        ]
    )
    if provenance["unresolved_external_references"]:
        lines.extend(f"- `{value}`" for value in provenance["unresolved_external_references"])
    else:
        lines.append("- None detected.")
    lines.extend(
        [
            "",
            "## Next evidence required",
            "",
            "1. Preserve the source commit and exact runtime manifest for every report.",
            "2. Supply the raw rollout and viewer-pose artifacts when a viewer or metric audit is required.",
            "3. Link each video to an explicit condition/seed record; do not infer pairings from filenames.",
            "4. Review the literature mappings manually before using any value as a calibration target.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path, help="Path to the supplied ZIP archive.")
    parser.add_argument(
        "--output",
        type=Path,
        default=REPOSITORY_ROOT / "reports" / "external_artifact_audit",
        help="Directory for audit.json and audit.md.",
    )
    parser.add_argument("--repo-root", type=Path, default=REPOSITORY_ROOT)
    args = parser.parse_args()
    report = audit_archive(args.archive, repo_root=args.repo_root, output_dir=args.output)
    print(f"Status: {report['status']}")
    print(f"Archive: {report['archive']['name']}")
    print(f"JSON reports: {report['inventory']['json_count']}")
    print(f"Videos: {report['inventory']['video_count']}")
    output = args.output.expanduser()
    if not output.is_absolute():
        output = args.repo_root.expanduser().resolve() / output
    print(f"Audit: {output.resolve()}")
    return 0 if report["status"] != "INVALID_ARCHIVE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
