"""Regression tests for the optional real brain-body integration runner."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_brain_body_rollout.py"
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import run_brain_body_rollout as runner  # noqa: E402


def test_missing_brain_source_stops_before_simulation(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    missing = tmp_path / "missing-phase-a"
    output = tmp_path / "output"
    status = runner.main(
        [
            "--brain-root",
            str(missing),
            "--steps",
            "1",
            "--output",
            str(output),
        ]
    )
    assert status == 2
    assert not output.exists()
    assert "brain source not found" in capsys.readouterr().err


def test_final_manifest_contains_only_real_files(tmp_path: Path) -> None:
    output = tmp_path / "run"
    output.mkdir()
    (output / "rollout.json").write_text("{}\n", encoding="utf-8")
    runner._write_final_manifest(output)
    manifest = json.loads((output / "brain_body_manifest.json").read_text(encoding="utf-8"))
    assert "rollout.json" in manifest["files"]
    assert "brain_body_manifest.json" not in manifest["files"]
    assert len(manifest["files"]["rollout.json"]["sha256"]) == 64


@pytest.mark.skipif(
    os.environ.get("RUN_BRAIN_BODY_INTEGRATION") != "1",
    reason="Set RUN_BRAIN_BODY_INTEGRATION=1 to run the real GPU/brain-body integration test.",
)
def test_real_brain_body_rollout_to_viewer_pose(tmp_path: Path) -> None:
    brain_root = Path(os.environ.get("FLY_BRAIN_ROOT", ROOT.parent / "phase-A-clean"))
    candidates = (
        Path(os.environ["FLY_BRAIN_PYTHON"])
        if os.environ.get("FLY_BRAIN_PYTHON")
        else brain_root / ".venv" / "Scripts" / "python.exe",
        brain_root / ".venv" / "bin" / "python",
    )
    brain_python = next((path for path in candidates if path.is_file()), None)
    if brain_python is None:
        pytest.skip("No brain-source Python environment is available.")
    output = tmp_path / "brain-body"
    result = subprocess.run(
        [
            str(brain_python),
            str(SCRIPT),
            "--brain-root",
            str(brain_root),
            "--steps",
            "10",
            "--seed",
            "0",
            "--device",
            "cuda",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    summary = json.loads((output / "brain_body_summary.json").read_text(encoding="utf-8"))
    pose = json.loads((output / "viewer_pose.json").read_text(encoding="utf-8"))
    assert summary["brain_device"] == "cuda"
    assert summary["frame_count"] == 11
    assert len(pose["frames"]) == 11
    first_bones = pose["frames"][0]["skeleton"]["bones"]
    assert any(any(abs(float(value)) > 0.0 for value in bone["position"]) for bone in first_bones)
    assert (output / "viewer_bundle.zip").is_file()
