"""Computational disease-signature comparison without biological inference."""

from .signature import DiseaseSignature, SIGNATURE_FIELDS, UNAVAILABLE
from .builder import build_signature, build_signature_from_directory, build_signature_from_files, load_signature
from .distance import (
    DistanceResult,
    cosine_distance,
    dynamic_time_warping_distance,
    earth_mover_distance,
    euclidean_distance,
    mahalanobis_distance,
    weighted_euclidean_distance,
)
from .embedding import SignatureEmbedding
from .matcher import MatchResult, MatchingReport, SignatureMatcher, match_signatures
from .normalization import NORMALIZATION_METHODS, NormalizationResult, normalize_signature, normalize_signatures
from .report import write_signature_reports
from .validation import validate_normalization_consistency, validate_signature, validate_signatures

__all__ = [
    "DiseaseSignature",
    "DistanceResult",
    "MatchResult",
    "MatchingReport",
    "NORMALIZATION_METHODS",
    "NormalizationResult",
    "SIGNATURE_FIELDS",
    "SignatureEmbedding",
    "SignatureMatcher",
    "UNAVAILABLE",
    "build_signature",
    "build_signature_from_directory",
    "build_signature_from_files",
    "cosine_distance",
    "dynamic_time_warping_distance",
    "earth_mover_distance",
    "euclidean_distance",
    "load_signature",
    "mahalanobis_distance",
    "match_signatures",
    "normalize_signature",
    "normalize_signatures",
    "validate_normalization_consistency",
    "validate_signature",
    "validate_signatures",
    "weighted_euclidean_distance",
    "write_signature_reports",
]
