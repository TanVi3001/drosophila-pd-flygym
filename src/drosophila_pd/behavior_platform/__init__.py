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
    "ExportRequest",
    "OfflineRenderRequest",
    "OfflineRenderResult",
    "RolloutData",
    "RolloutExportResult",
    "ViewerPlan",
    "build_comparison_playback_plan",
    "build_viewer_plan",
    "compare_rollouts",
    "export_rollout_package",
    "measure_rollout_behavior",
    "render_offline",
]
