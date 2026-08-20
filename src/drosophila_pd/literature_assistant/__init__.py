"""Human-in-the-loop literature curation assistant.

This package parses only explicit, structured candidate fields. It does not
crawl, download, infer phenotypes, or write the Digital Phenotype Atlas.
"""

from .candidate import CANDIDATE_FIELDS, CandidatePhenotype
from .parser import SUPPORTED_SUFFIXES, parse_source
from .report import write_review_reports
from .review import ReviewStore, ReviewStatus
from .validation import validate_candidate, validate_candidates
from .workflow import LiteratureAssistantWorkflow

__all__ = [
    "CANDIDATE_FIELDS",
    "CandidatePhenotype",
    "LiteratureAssistantWorkflow",
    "ReviewStatus",
    "ReviewStore",
    "SUPPORTED_SUFFIXES",
    "parse_source",
    "validate_candidate",
    "validate_candidates",
    "write_review_reports",
]
