"""Contract checks for the additive pose-viewer transition layer."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
VIEWER = ROOT / "web" / "viewer"
VIEWER_FILES = (
    "pose_loader.js",
    "skeleton_animator.js",
    "camera_controller.js",
    "playback_controller.js",
    "scene_builder.js",
    "trajectory_renderer.js",
    "digital_fly_viewer.js",
)


def test_viewer_skeleton_files_exist_without_new_rendering_framework() -> None:
    for filename in VIEWER_FILES:
        text = (VIEWER / filename).read_text(encoding="utf-8")
        assert "export" in text
        assert "three" not in text.lower()
        assert "babylon" not in text.lower()


def test_pose_schema_is_explicit_and_data_free() -> None:
    schema_path = ROOT / "docs" / "api" / "viewer_pose.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["required"] == ["metadata", "fps", "frame_count", "frames"]
    frame_required = schema["properties"]["frames"]["items"]["required"]
    assert frame_required == [
        "thorax",
        "orientation",
        "COM",
        "joint_angles",
        "joint_velocities",
        "contacts",
        "trajectory",
    ]
    assert "example" not in schema


def test_rest_preparation_is_documentation_only() -> None:
    text = (ROOT / "docs" / "api" / "rest_api.md").read_text(encoding="utf-8")
    for endpoint in (
        "GET | `/datasets`",
        "GET | `/dataset/{id}`",
        "GET | `/rollout/{id}`",
        "GET | `/viewer/{id}`",
        "POST | `/analysis`",
        "POST | `/statistics`",
        "POST | `/validation`",
        "GET | `/report/{id}`",
    ):
        assert endpoint in text
    assert "no server implementation" in text.lower()


def test_vietnamese_transition_documents_exist() -> None:
    for number, stem in (
        ("70", "Kien_Truc_Tong_The"),
        ("71", "Digital_Laboratory"),
        ("72", "Web_Viewer"),
        ("73", "Roadmap_Web"),
        ("74", "Module_Map"),
        ("75", "Cleanup_Report"),
    ):
        assert (ROOT / "docs" / "vi" / f"{number}_{stem}.md").is_file()
