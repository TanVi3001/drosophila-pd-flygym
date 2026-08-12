"""Version 2 behavioral platform for rollout post-processing.

The package is additive to the frozen v1 implementation. It operates on
already-produced rollout arrays and does not run FlyGym/MuJoCo simulations,
modify controllers, or introduce perturbations.
"""

from drosophila_pd.behavior_platform.comparison import (
    ComparisonCondition,
    ComparisonPlaybackPlan,
    build_comparison_playback_plan,
    compare_rollouts,
)
from drosophila_pd.behavior_platform.behavior_comparison import compare_behavior_conditions
from drosophila_pd.behavior_platform.dashboard import (
    DASHBOARD_EXPORT_FORMATS,
    build_behavior_dashboard,
    export_behavior_dashboard,
    plot_trajectory_explorer,
)
from drosophila_pd.behavior_platform.data_model import (
    Arena,
    ArenaZone,
    BehaviorComparison,
    BehaviorDashboard,
    BehaviorEpisode,
    BehaviorReport,
    BehaviorSequence,
    ProgressionStage,
    ProgressionTimeline,
)
from drosophila_pd.behavior_platform.export import (
    ExportRequest,
    RolloutExportResult,
    export_rollout_package,
)
from drosophila_pd.behavior_platform.gait import (
    CANONICAL_LEG_ORDER,
    GaitAnalysisConfig,
    GaitInput,
    analyze_gait,
)
from drosophila_pd.behavior_platform.gait_animation import (
    GaitAnimationRequest,
    GaitAnimationResult,
    render_gait_animation,
)
from drosophila_pd.behavior_platform.gait_export import (
    GaitExportRequest,
    GaitExportResult,
    export_gait_package,
)
from drosophila_pd.behavior_platform.gait_visualization import (
    plot_contact_raster,
    plot_coordination_matrix,
    plot_foot_trajectories,
    plot_footfall_diagram,
    plot_gait_timeline,
    plot_joint_trajectories,
    plot_phase_wheel,
    plot_stride_plot,
    render_gait_visualization_set,
)
from drosophila_pd.behavior_platform.measurement import (
    DEFAULT_BEHAVIOR_MEASUREMENT_CONFIG,
    measure_rollout_behavior,
)
from drosophila_pd.behavior_platform.open_field import (
    analyze_open_field,
    export_open_field_report,
)
from drosophila_pd.behavior_platform.progression import (
    interpolate_stages,
    interpolated_stage_at,
    progression_from_config,
    progression_to_json,
    replay_progression,
    stage_at,
)
from drosophila_pd.behavior_platform.rendering import (
    OfflineRenderRequest,
    OfflineRenderResult,
    render_offline,
)
from drosophila_pd.behavior_platform.rollout import RolloutData
from drosophila_pd.behavior_platform.visualization import (
    CameraPreset,
    ViewerPlan,
    build_viewer_plan,
)
from drosophila_pd.behavior_platform.video_system import (
    VIDEO_EXPORT_FORMATS,
    PlaybackOverlayConfig,
    SynchronizedPlaybackRequest,
    SynchronizedPlaybackResult,
    render_synchronized_playback,
)

__all__ = [
    "Arena",
    "ArenaZone",
    "BehaviorComparison",
    "BehaviorDashboard",
    "BehaviorEpisode",
    "BehaviorReport",
    "BehaviorSequence",
    "CameraPreset",
    "ComparisonCondition",
    "ComparisonPlaybackPlan",
    "DASHBOARD_EXPORT_FORMATS",
    "DEFAULT_BEHAVIOR_MEASUREMENT_CONFIG",
    "CANONICAL_LEG_ORDER",
    "ExportRequest",
    "GaitAnalysisConfig",
    "GaitAnimationRequest",
    "GaitAnimationResult",
    "GaitExportRequest",
    "GaitExportResult",
    "GaitInput",
    "OfflineRenderRequest",
    "OfflineRenderResult",
    "PlaybackOverlayConfig",
    "ProgressionStage",
    "ProgressionTimeline",
    "RolloutData",
    "RolloutExportResult",
    "SynchronizedPlaybackRequest",
    "SynchronizedPlaybackResult",
    "VIDEO_EXPORT_FORMATS",
    "ViewerPlan",
    "analyze_gait",
    "analyze_open_field",
    "build_behavior_dashboard",
    "build_comparison_playback_plan",
    "build_viewer_plan",
    "compare_behavior_conditions",
    "compare_rollouts",
    "export_behavior_dashboard",
    "export_gait_package",
    "export_open_field_report",
    "export_rollout_package",
    "interpolate_stages",
    "interpolated_stage_at",
    "measure_rollout_behavior",
    "plot_contact_raster",
    "plot_coordination_matrix",
    "plot_foot_trajectories",
    "plot_footfall_diagram",
    "plot_gait_timeline",
    "plot_joint_trajectories",
    "plot_phase_wheel",
    "plot_stride_plot",
    "plot_trajectory_explorer",
    "progression_from_config",
    "progression_to_json",
    "render_synchronized_playback",
    "render_gait_animation",
    "render_gait_visualization_set",
    "render_offline",
    "replay_progression",
    "stage_at",
]
