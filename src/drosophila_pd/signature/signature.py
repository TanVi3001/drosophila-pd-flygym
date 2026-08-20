"""Data model for declared computational phenotype signatures."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Mapping


UNAVAILABLE = "unavailable"

SIGNATURE_FIELDS = (
    "walking_speed",
    "stride_length",
    "step_frequency",
    "pause_fraction",
    "heading_variance",
    "turning_rate",
    "symmetry_index",
    "trajectory_efficiency",
    "orientation_stability",
    "joint_velocity_mean",
    "joint_velocity_std",
    "com_displacement",
    "path_length",
)

SignatureValue = float | str


@dataclass(frozen=True)
class DiseaseSignature:
    """One computational signature with unavailable values kept explicit.

    The metric fields are intentionally required at construction time. Missing
    observations must be represented by :data:`UNAVAILABLE`, never by a
    fabricated numeric default.
    """

    walking_speed: SignatureValue
    stride_length: SignatureValue
    step_frequency: SignatureValue
    pause_fraction: SignatureValue
    heading_variance: SignatureValue
    turning_rate: SignatureValue
    symmetry_index: SignatureValue
    trajectory_efficiency: SignatureValue
    orientation_stability: SignatureValue
    joint_velocity_mean: SignatureValue
    joint_velocity_std: SignatureValue
    com_displacement: SignatureValue
    path_length: SignatureValue
    signature_id: str | None = None
    source: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name in SIGNATURE_FIELDS:
            value = getattr(self, field_name)
            if value == UNAVAILABLE:
                continue
            try:
                converted = float(value)
            except (TypeError, ValueError) as error:
                raise ValueError(f"{field_name} must be finite numeric or '{UNAVAILABLE}'.") from error
            if not math.isfinite(converted):
                raise ValueError(f"{field_name} must be finite numeric or '{UNAVAILABLE}'.")
            object.__setattr__(self, field_name, converted)
        object.__setattr__(self, "source", tuple(str(item) for item in self.source))
        object.__setattr__(self, "metadata", dict(self.metadata))

    @classmethod
    def from_mapping(
        cls,
        mapping: Mapping[str, Any],
        *,
        signature_id: str | None = None,
        source: tuple[str, ...] | list[str] = (),
        metadata: Mapping[str, Any] | None = None,
    ) -> "DiseaseSignature":
        values = mapping.get("values") if isinstance(mapping.get("values"), Mapping) else mapping
        identifier = signature_id or _text(values.get("signature_id")) or _text(values.get("dataset_id"))
        effective_source = tuple(source) or _source_from_mapping(mapping)
        effective_metadata = dict(metadata or {})
        if isinstance(mapping.get("metadata"), Mapping):
            effective_metadata = {**mapping["metadata"], **effective_metadata}
        return cls(
            **{field_name: _value(values.get(field_name, UNAVAILABLE)) for field_name in SIGNATURE_FIELDS},
            signature_id=identifier,
            source=effective_source,
            metadata=effective_metadata,
        )

    @property
    def available_fields(self) -> tuple[str, ...]:
        return tuple(field_name for field_name in SIGNATURE_FIELDS if self.value(field_name) != UNAVAILABLE)

    @property
    def missing_fields(self) -> tuple[str, ...]:
        return tuple(field_name for field_name in SIGNATURE_FIELDS if self.value(field_name) == UNAVAILABLE)

    def value(self, field_name: str) -> SignatureValue:
        if field_name not in SIGNATURE_FIELDS:
            raise ValueError(f"Unsupported signature field: {field_name}")
        return getattr(self, field_name)

    def values(self) -> dict[str, SignatureValue]:
        return {field_name: self.value(field_name) for field_name in SIGNATURE_FIELDS}

    def to_mapping(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "signature_id": self.signature_id,
            "values": self.values(),
            "source": list(self.source),
            "metadata": dict(self.metadata),
            "scientific_scope": (
                "Computational phenotype signature for concordance analysis; "
                "not a medical conclusion, disease stage, or biological disease state."
            ),
        }


def _value(value: Any) -> SignatureValue:
    if value in (None, "", UNAVAILABLE):
        return UNAVAILABLE
    return value


def _text(value: Any) -> str | None:
    return None if value in (None, "") else str(value)


def _source_from_mapping(mapping: Mapping[str, Any]) -> tuple[str, ...]:
    source = mapping.get("source")
    if isinstance(source, (list, tuple)):
        return tuple(str(item) for item in source)
    return (str(source),) if source not in (None, "") else ()


__all__ = ["DiseaseSignature", "SIGNATURE_FIELDS", "SignatureValue", "UNAVAILABLE"]
