"""Visualization metadata and deployment helpers for the Three.js mesh layer.

When the rollout contains the canonical NeuroMechFly body-segment names and the
installed FlyGym package exposes its bundled STL assets, the exporter declares
those real assets. Other rollout shapes retain the explicitly labeled
presentation fallback. No mesh vertices or scientific body measurements are
synthesized here.
"""

from __future__ import annotations

import importlib.metadata
from pathlib import Path
import shutil
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

DEFAULT_BODY_HIERARCHY = (
    {"id": "fly", "parent": None, "children": ("thorax",), "role": "display_root"},
    {
        "id": "thorax",
        "parent": "fly",
        "children": (
            "head",
            "abdomen",
            "wing_L",
            "wing_R",
            "leg_FL",
            "leg_ML",
            "leg_HL",
            "leg_FR",
            "leg_MR",
            "leg_HR",
        ),
        "role": "display_body_segment",
    },
    {"id": "head", "parent": "thorax", "children": ("eye_L", "eye_R", "antenna_L", "antenna_R"), "role": "display_body_segment"},
    {"id": "abdomen", "parent": "thorax", "children": (), "role": "display_body_segment"},
    {"id": "wing_L", "parent": "thorax", "children": (), "role": "display_appendage"},
    {"id": "wing_R", "parent": "thorax", "children": (), "role": "display_appendage"},
    {"id": "leg_FL", "parent": "thorax", "children": (), "role": "display_appendage"},
    {"id": "leg_ML", "parent": "thorax", "children": (), "role": "display_appendage"},
    {"id": "leg_HL", "parent": "thorax", "children": (), "role": "display_appendage"},
    {"id": "leg_FR", "parent": "thorax", "children": (), "role": "display_appendage"},
    {"id": "leg_MR", "parent": "thorax", "children": (), "role": "display_appendage"},
    {"id": "leg_HR", "parent": "thorax", "children": (), "role": "display_appendage"},
    {"id": "eye_L", "parent": "head", "children": (), "role": "display_detail"},
    {"id": "eye_R", "parent": "head", "children": (), "role": "display_detail"},
    {"id": "antenna_L", "parent": "head", "children": (), "role": "display_detail"},
    {"id": "antenna_R", "parent": "head", "children": (), "role": "display_detail"},
)

DEFAULT_DISPLAY_SEGMENTS = (
    {"id": "thorax", "label": "Thorax", "primitive": "ellipsoid", "material": "thorax"},
    {"id": "abdomen", "label": "Abdomen", "primitive": "ellipsoid", "material": "abdomen"},
    {"id": "head", "label": "Head", "primitive": "ellipsoid", "material": "head"},
    {"id": "wing_L", "label": "Left wing", "primitive": "transparent_wing", "material": "wing"},
    {"id": "wing_R", "label": "Right wing", "primitive": "transparent_wing", "material": "wing"},
    {"id": "leg_FL", "label": "Front left leg", "primitive": "segmented_cylinder", "material": "leg"},
    {"id": "leg_ML", "label": "Middle left leg", "primitive": "segmented_cylinder", "material": "leg"},
    {"id": "leg_HL", "label": "Hind left leg", "primitive": "segmented_cylinder", "material": "leg"},
    {"id": "leg_FR", "label": "Front right leg", "primitive": "segmented_cylinder", "material": "leg"},
    {"id": "leg_MR", "label": "Middle right leg", "primitive": "segmented_cylinder", "material": "leg"},
    {"id": "leg_HR", "label": "Hind right leg", "primitive": "segmented_cylinder", "material": "leg"},
)

DEFAULT_DISPLAY_MATERIALS = {
    "thorax": {"color": "#d08a53", "roughness": 0.82, "metalness": 0.02},
    "abdomen": {"color": "#7c5039", "roughness": 0.88, "metalness": 0.02},
    "head": {"color": "#c98c5f", "roughness": 0.8, "metalness": 0.02},
    "eye": {"color": "#23130f", "roughness": 0.45, "metalness": 0.0},
    "wing": {"color": "#bfe6f5", "roughness": 0.35, "metalness": 0.0, "opacity": 0.42},
    "leg": {"color": "#3d2c24", "roughness": 0.9, "metalness": 0.0},
    "antenna": {"color": "#4a2f25", "roughness": 0.86, "metalness": 0.0},
}


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
    body_segment_names: Iterable[str] = (),
) -> dict[str, Any]:
    """Return mesh metadata for a viewer pose document."""

    body_segments = [str(name) for name in body_segment_names]
    flygym_asset = _build_flygym_mesh_asset(body_segments)
    if flygym_asset is not None:
        return {
            "renderer": "web/viewer/digital_fly_mesh.js",
            "render_mode": "flygym_stl",
            "scientific_mesh": True,
            "asset": flygym_asset,
            "asset_status": "available_from_flygym",
            "fallback_reason": None,
            "body_parts": list(DEFAULT_VIEWER_BODY_PARTS),
            "body_segment_names": body_segments,
            "body_hierarchy": _json_ready(DEFAULT_BODY_HIERARCHY),
            "segments": _json_ready(DEFAULT_DISPLAY_SEGMENTS),
            "mesh_instances": _json_ready(flygym_asset["segments"]),
            "bones": [
                {"id": item["id"], "parent": item["parent"], "source": "rollout.body_positions"}
                for item in DEFAULT_BODY_HIERARCHY
                if item["parent"] is not None
            ],
            "materials": _json_ready(DEFAULT_DISPLAY_MATERIALS),
            "joint_names": [str(name) for name in joint_names],
            "visibility": dict(visibility),
            "scientific_scope": (
                "FlyGym NeuroMechFly mesh assets driven by recorded body poses. "
                "The visualization does not add biological measurements or validation."
            ),
        }
    return {
        "renderer": "web/viewer/digital_fly_mesh.js",
        "render_mode": "procedural_fallback",
        "scientific_mesh": False,
        "asset": None,
        "asset_status": "not_in_repository",
        "fallback_reason": (
            "No anatomical fly mesh asset is present in the repository. "
            "The viewer uses a presentation mesh driven by real rollout pose data."
        ),
        "body_parts": list(DEFAULT_VIEWER_BODY_PARTS),
        "body_segment_names": body_segments,
        "body_hierarchy": _json_ready(DEFAULT_BODY_HIERARCHY),
        "segments": _json_ready(DEFAULT_DISPLAY_SEGMENTS),
        "mesh_instances": [
            {
                "id": f"{segment['id']}_mesh",
                "segment": segment["id"],
                "source": "procedural_fallback",
                "scientific_mesh": False,
            }
            for segment in DEFAULT_DISPLAY_SEGMENTS
        ],
        "bones": [
            {"id": item["id"], "parent": item["parent"], "source": "display_hierarchy"}
            for item in DEFAULT_BODY_HIERARCHY
            if item["parent"] is not None
        ],
        "materials": _json_ready(DEFAULT_DISPLAY_MATERIALS),
        "joint_names": [str(name) for name in joint_names],
        "visibility": dict(visibility),
        "scientific_scope": (
            "Display metadata only. This is not an anatomical mesh export and "
            "does not add biological measurements."
        ),
    }


def materialize_mesh_assets(mesh: dict[str, Any], output_root: str | Path) -> list[Path]:
    """Copy declared FlyGym mesh assets next to an exported pose document.

    The installed FlyGym package remains the source of truth.  The copied files
    are deployment assets only, so a static viewer bundle does not depend on the
    Python environment that produced the rollout.
    """

    asset = mesh.get("asset") if isinstance(mesh, dict) else None
    if not isinstance(asset, dict) or asset.get("type") != "stl_segments":
        return []
    mesh_dir = _find_flygym_mesh_dir()
    if mesh_dir is None:
        raise FileNotFoundError("FlyGym NeuroMechFly mesh assets are unavailable")

    output = Path(output_root).resolve()
    copied: list[Path] = []
    seen_destinations: set[Path] = set()
    for item in asset.get("segments", []):
        if not isinstance(item, dict):
            continue
        uri = item.get("uri")
        source_segment = item.get("source_segment")
        if not isinstance(uri, str) or not isinstance(source_segment, str):
            continue
        source = mesh_dir / f"{source_segment}.stl"
        if not source.is_file():
            raise FileNotFoundError(f"FlyGym mesh asset is missing: {source}")
        destination = output / _safe_relative_path(uri)
        if destination in seen_destinations:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append(destination)
        seen_destinations.add(destination)
    return copied


def _build_flygym_mesh_asset(body_segments: list[str]) -> dict[str, Any] | None:
    required = {"c_thorax", "c_head", "lf_coxa", "lm_coxa", "lh_coxa", "rf_coxa", "rm_coxa", "rh_coxa"}
    if not required.issubset(body_segments):
        return None
    mesh_dir = _find_flygym_mesh_dir()
    if mesh_dir is None:
        return None

    segments = []
    seen_uris: set[str] = set()
    for name in body_segments:
        source_segment = f"l{name[1:]}" if name.startswith("r") else name
        source = mesh_dir / f"{source_segment}.stl"
        if not source.is_file():
            return None
        uri = f"assets/flygym/neuromechfly/simplified_max2000faces/{source_segment}.stl"
        item = {
            "id": name,
            "segment": name,
            "uri": uri,
            "source_segment": source_segment,
            "mirror_y": name.startswith("r"),
            "scale": [1000.0, -1000.0 if name.startswith("r") else 1000.0, 1000.0],
            "material": _material_for_segment(name),
        }
        segments.append(item)
        if uri not in seen_uris:
            seen_uris.add(uri)

    try:
        version = importlib.metadata.version("flygym")
    except importlib.metadata.PackageNotFoundError:
        version = "unknown"
    return {
        "type": "stl_segments",
        "format": "stl",
        "source": "FlyGym NeuroMechFly simplified_max2000faces",
        "source_package": "flygym",
        "source_version": version,
        "scale_units": "millimetres",
        "files": sorted(seen_uris),
        "segments": segments,
    }


def _find_flygym_mesh_dir() -> Path | None:
    try:
        import flygym
    except ModuleNotFoundError:
        return None
    package_root = Path(flygym.__file__).resolve().parent
    candidate = package_root / "assets" / "model" / "neuromechfly" / "meshes" / "simplified_max2000faces"
    return candidate if candidate.is_dir() else None


def _safe_relative_path(value: str) -> Path:
    path = Path(*value.replace("\\", "/").split("/"))
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Mesh asset URI must be relative: {value}")
    return path


def _material_for_segment(name: str) -> str:
    if name.startswith(("l_eye", "r_eye")):
        return "eye"
    if name.startswith(("l_wing", "r_wing")):
        return "wing"
    if name.startswith(("l_", "r_")):
        return "leg" if any(token in name for token in ("coxa", "trochanter", "tibia", "tarsus")) else "antenna"
    if "abdomen" in name:
        return "abdomen"
    if name in {"c_head", "c_rostrum", "c_haustellum"}:
        return "head"
    return "thorax"


def _json_ready(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    return value


__all__ = [
    "DEFAULT_VIEWER_BODY_PARTS",
    "build_mesh_metadata",
    "build_visibility",
    "materialize_mesh_assets",
]
