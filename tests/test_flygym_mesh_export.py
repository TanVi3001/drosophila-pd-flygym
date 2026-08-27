from __future__ import annotations

from pathlib import Path

import pytest

from drosophila_pd.viewer_export import build_mesh_metadata, materialize_mesh_assets


def test_installed_flygym_neuromechfly_mesh_is_exportable(tmp_path: Path) -> None:
    pytest.importorskip("flygym")
    from flygym.compose.fly.neuromechfly import ALL_SEGMENT_NAMES

    mesh = build_mesh_metadata(
        joint_names=[],
        visibility={"mesh": True, "skeleton": True, "trajectory": True, "COM": True},
        body_segment_names=ALL_SEGMENT_NAMES,
    )

    assert mesh["render_mode"] == "flygym_stl"
    assert mesh["scientific_mesh"] is True
    assert mesh["asset"]["type"] == "stl_segments"
    assert len(mesh["asset"]["segments"]) == len(ALL_SEGMENT_NAMES)

    copied = materialize_mesh_assets(mesh, tmp_path)

    assert copied
    assert all(path.is_file() for path in copied)
    assert all(path.relative_to(tmp_path).as_posix().startswith("assets/flygym/") for path in copied)


def test_non_neuromechfly_rollouts_keep_presentation_fallback() -> None:
    mesh = build_mesh_metadata(
        joint_names=[],
        visibility={"mesh": True, "skeleton": False, "trajectory": True, "COM": False},
        body_segment_names=["thorax", "head"],
    )

    assert mesh["render_mode"] == "procedural_fallback"
    assert mesh["scientific_mesh"] is False
    assert mesh["asset"] is None
