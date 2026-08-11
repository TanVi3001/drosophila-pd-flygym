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

__all__ = [
    "CameraPreset",
    "ComparisonCondition",
    "ComparisonPlaybackPlan",
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
    "RolloutData",
    "RolloutExportResult",
    "ViewerPlan",
    "analyze_gait",
    "build_comparison_playback_plan",
    "build_viewer_plan",
    "compare_rollouts",
    "export_gait_package",
    "export_rollout_package",
    "measure_rollout_behavior",
    "plot_contact_raster",
    "plot_coordination_matrix",
    "plot_foot_trajectories",
    "plot_footfall_diagram",
    "plot_gait_timeline",
    "plot_joint_trajectories",
    "plot_phase_wheel",
    "plot_stride_plot",
    "render_gait_animation",
    "render_gait_visualization_set",
    "render_offline",
]
