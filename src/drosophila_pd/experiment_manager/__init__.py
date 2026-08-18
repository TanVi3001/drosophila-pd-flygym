"""Sequential experiment-suite orchestration over imported rollout datasets.

The manager is an operational layer over :mod:`drosophila_pd.analysis`.  It
does not run FlyGym, create rollout data, or infer biological conclusions.
"""

from .config import ExperimentConfig, load_experiment_configs
from .manager import (
    EXPERIMENT_STATUSES,
    ExperimentManager,
    ExperimentRecord,
    run_experiment_suite,
)

__all__ = [
    "EXPERIMENT_STATUSES",
    "ExperimentConfig",
    "ExperimentManager",
    "ExperimentRecord",
    "load_experiment_configs",
    "run_experiment_suite",
]
