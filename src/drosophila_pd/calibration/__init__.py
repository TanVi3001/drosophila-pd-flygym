"""Literature-constrained computational phenotype calibration.

The package scores supplied simulation metrics against provenance-bearing
literature records. It does not run simulations, infer biology, or invent
missing targets.
"""

from .calibration_engine import (
    CalibrationCandidate,
    CalibrationEngine,
    CalibrationRun,
    load_simulation_metrics,
)
from .objective_functions import (
    ObjectiveFunction,
    ObjectiveResult,
    SUPPORTED_OBJECTIVES,
    compute_loss,
)
from .optimizer import (
    GridSearchOptimizer,
    Optimizer,
    OptimizerResult,
    available_optimizers,
)
from .parameter_space import ParameterDefinition, ParameterSpace, ParameterSpaceError
from .phenotype_database import (
    LITERATURE_FIELDS,
    LiteratureRecord,
    literature_records_to_targets,
    load_literature_csv,
    validate_literature_records,
)
from .report import write_calibration_reports
from .validation import validate_calibration_run
from .validation import (
    bootstrap_ci,
    leave_one_condition_out,
    leave_one_paper_out,
    mae,
    pearson,
    r_squared,
    rmse,
    spearman,
)

__all__ = [
    "CalibrationCandidate",
    "CalibrationEngine",
    "CalibrationRun",
    "GridSearchOptimizer",
    "LITERATURE_FIELDS",
    "LiteratureRecord",
    "ObjectiveFunction",
    "ObjectiveResult",
    "Optimizer",
    "OptimizerResult",
    "ParameterDefinition",
    "ParameterSpace",
    "ParameterSpaceError",
    "SUPPORTED_OBJECTIVES",
    "available_optimizers",
    "compute_loss",
    "bootstrap_ci",
    "leave_one_condition_out",
    "leave_one_paper_out",
    "mae",
    "pearson",
    "r_squared",
    "rmse",
    "spearman",
    "literature_records_to_targets",
    "load_literature_csv",
    "load_simulation_metrics",
    "validate_calibration_run",
    "validate_literature_records",
    "write_calibration_reports",
]
