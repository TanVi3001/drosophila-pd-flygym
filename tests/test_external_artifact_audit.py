"""Regression tests for read-only external artifact auditing."""

from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZipFile

from scripts.audit_external_artifacts import audit_archive


def _write_archive(path: Path, *, malformed: bool = False, unsafe: bool = False) -> None:
    report = {
        "experiment_id": "example",
        "model": "example_condition",
        "perturbation": {"source": "bridge_scales.json from fly-brain"},
        "baseline": {
            "git_commit": None,
            "environment": {"flygym_version": "2.1.0", "mujoco_version": "3.9.0"},
            "configuration": {"random_seed": 7},
            "derived_locomotion_metrics": {
                "sample_count": 101,
                "step_count": 100,
                "timestep_s": 0.001,
                "mean_planar_speed_mm_s": 10.0,
            },
            "scientific_scope": "Computational output only.",
        },
        "perturbed": {
            "derived_locomotion_metrics": {
                "sample_count": 101,
                "step_count": 100,
                "timestep_s": 0.001,
                "mean_planar_speed_mm_s": 8.0,
            },
            "scientific_scope": "Computational output only.",
        },
        "comparison": {},
        "overall_pass": True,
    }
    with ZipFile(path, "w") as archive:
        archive.writestr("example_locomotion.json", "{bad" if malformed else json.dumps(report))
        archive.writestr("example.mp4", b"video-bytes")
        if unsafe:
            archive.writestr("../outside.txt", b"must-not-extract")


def test_audit_inventories_and_parses_derived_archive(tmp_path: Path) -> None:
    archive = tmp_path / "artifacts.zip"
    output = tmp_path / "audit"
    _write_archive(archive)

    report = audit_archive(archive, repo_root=tmp_path, output_dir=output)

    assert report["status"] == "PARSEABLE_DERIVED_ARTIFACTS"
    assert report["inventory"]["json_count"] == 1
    assert report["inventory"]["video_count"] == 1
    assert report["inventory"]["raw_rollout_members"] == []
    assert report["provenance"]["viewer_pose_present"] is False
    assert report["json_reports"][0]["metrics"]["baseline_sample_count"] == 101
    assert report["json_reports"][0]["random_seed"] == 7
    assert report["json_reports"][0]["git_commit"] is None
    assert "bridge_scales" in report["provenance"]["unresolved_external_references"][0]
    assert (output / "audit.json").is_file()
    assert (output / "audit.md").is_file()


def test_audit_rejects_malformed_json(tmp_path: Path) -> None:
    archive = tmp_path / "malformed.zip"
    _write_archive(archive, malformed=True)

    report = audit_archive(archive, repo_root=tmp_path)

    assert report["status"] == "INVALID_ARCHIVE"
    assert report["inventory"]["invalid_json_members"] == ["example_locomotion.json"]


def test_audit_rejects_unsafe_member_without_extracting(tmp_path: Path) -> None:
    archive = tmp_path / "unsafe.zip"
    _write_archive(archive, unsafe=True)

    report = audit_archive(archive, repo_root=tmp_path)

    assert report["status"] == "INVALID_ARCHIVE"
    assert report["inventory"]["unsafe_members"] == ["../outside.txt"]


def test_audit_rejects_windows_drive_member(tmp_path: Path) -> None:
    archive = tmp_path / "windows-unsafe.zip"
    with ZipFile(archive, "w") as handle:
        handle.writestr(r"C:\outside.txt", b"must-not-extract")

    report = audit_archive(archive, repo_root=tmp_path)

    assert report["status"] == "INVALID_ARCHIVE"
    assert report["inventory"]["unsafe_members"] == ["C:/outside.txt"]
