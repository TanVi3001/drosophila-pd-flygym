"""Read-only FlyGym rollout to Three.js viewer-pose export package."""

from .mesh_exporter import DEFAULT_VIEWER_BODY_PARTS, build_mesh_metadata, build_visibility
from .pose_exporter import (
    PoseExportResult,
    RolloutInputs,
    build_viewer_pose,
    export_viewer_pose,
    load_rollout_inputs,
    resolve_dataset,
)
from .schema import FRAME_SCHEMA, VIEWER_POSE_SCHEMA, schema
from .trajectory_exporter import build_trajectory_frames, trajectory_for_frame
from .validator import PoseValidationError, ValidationReport, validate_pose_document

__all__ = [
    "DEFAULT_VIEWER_BODY_PARTS",
    "FRAME_SCHEMA",
    "PoseExportResult",
    "PoseValidationError",
    "RolloutInputs",
    "VIEWER_POSE_SCHEMA",
    "ValidationReport",
    "build_mesh_metadata",
    "build_trajectory_frames",
    "build_viewer_pose",
    "build_visibility",
    "export_viewer_pose",
    "load_rollout_inputs",
    "resolve_dataset",
    "schema",
    "trajectory_for_frame",
    "validate_pose_document",
]
