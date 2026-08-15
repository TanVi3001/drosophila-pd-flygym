"""Visualization metadata helpers for the existing Three.js mesh.

This module does not synthesize mesh coordinates or scientific body data. It
only records which source channels are available to the already implemented
viewer and its default presentation mesh.
"""

from __future__ import annotations

from typing import Any, Iterable


DEFAULT_VIEWER_BODY_PARTS = (
    "head",
    "thorax",
    "abdomen",
    "eyes",
    "antenna",
    "wings",
    "legs",
)


def build_visibility(
    *,
    has_joint_data: bool,
    has_com_data: bool,
    has_trajectory_data: bool = True,
) -> dict[str, bool]:
    """Describe renderable overlays based only on available source channels."""

    return {
        "mesh": True,
        "skeleton": bool(has_joint_data),
        "COM": bool(has_com_data),
        "trajectory": bool(has_trajectory_data),
    }


def build_mesh_metadata(
    *,
    joint_names: Iterable[str],
    visibility: dict[str, bool],
) -> dict[str, Any]:
    """Return non-scientific display metadata for a viewer pose document."""

    return {
        "renderer": "web/viewer/digital_fly_mesh.js",
        "body_parts": list(DEFAULT_VIEWER_BODY_PARTS),
        "joint_names": [str(name) for name in joint_names],
        "visibility": dict(visibility),
        "scientific_scope": "Display metadata only; no anatomical mesh measurements are added.",
    }


__all__ = ["DEFAULT_VIEWER_BODY_PARTS", "build_mesh_metadata", "build_visibility"]
