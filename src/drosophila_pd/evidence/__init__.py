"""Literature Evidence Engine for Disease Layer preparation.

The package consumes curation artifacts and reports evidence completeness,
proxy coverage and metric-to-proxy mappings. It never runs FlyGym or changes
scientific model parameters.
"""

from .coverage import compute_coverage
from .dependency import build_dependency_rows, build_disease_layer_matrix
from .importance import rank_proxy_importance
from .models import (
    CONFIDENCE_WEIGHTS,
    EXPECTED_PROXIES,
    CoverageRow,
    DependencyRow,
    EvidenceBundle,
    EvidenceCriterion,
    EvidenceScore,
    ImportanceRow,
    MappingEvidence,
    PaperEvidence,
    ScoringConfig,
)
from .report import build_evidence_bundle, run_evidence_engine, write_evidence_reports
from .scoring import default_scoring_config, load_scoring_config, score_paper, score_papers
from .validation import EvidenceValidationError, load_evidence_inputs, validate_loaded_inputs

__all__ = [
    "CONFIDENCE_WEIGHTS",
    "EXPECTED_PROXIES",
    "CoverageRow",
    "DependencyRow",
    "EvidenceBundle",
    "EvidenceCriterion",
    "EvidenceScore",
    "EvidenceValidationError",
    "ImportanceRow",
    "MappingEvidence",
    "PaperEvidence",
    "ScoringConfig",
    "build_dependency_rows",
    "build_disease_layer_matrix",
    "build_evidence_bundle",
    "compute_coverage",
    "default_scoring_config",
    "load_evidence_inputs",
    "load_scoring_config",
    "rank_proxy_importance",
    "run_evidence_engine",
    "score_paper",
    "score_papers",
    "validate_loaded_inputs",
    "write_evidence_reports",
]
