"""Vector storage abstraction for future signature representations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .signature import DiseaseSignature, SIGNATURE_FIELDS, UNAVAILABLE


@dataclass(frozen=True)
class SignatureEmbedding:
    """A plain metric vector; no deep learning, PCA, or UMAP is applied."""

    fields: tuple[str, ...]
    vector: tuple[float | None, ...]
    mask: tuple[bool, ...]
    signature_id: str | None = None
    method: str = "raw"

    @classmethod
    def from_signature(cls, signature: DiseaseSignature, *, method: str = "raw") -> "SignatureEmbedding":
        vector: list[float | None] = []
        mask: list[bool] = []
        for field_name in SIGNATURE_FIELDS:
            value = signature.value(field_name)
            available = value != UNAVAILABLE
            vector.append(float(value) if available else None)
            mask.append(available)
        return cls(
            fields=SIGNATURE_FIELDS,
            vector=tuple(vector),
            mask=tuple(mask),
            signature_id=signature.signature_id,
            method=method,
        )

    @property
    def available_fields(self) -> tuple[str, ...]:
        return tuple(field_name for field_name, available in zip(self.fields, self.mask) if available)

    def field_values(self) -> dict[str, float | None]:
        return dict(zip(self.fields, self.vector))

    def to_mapping(self) -> dict[str, Any]:
        return {
            "signature_id": self.signature_id,
            "method": self.method,
            "fields": list(self.fields),
            "vector": list(self.vector),
            "mask": list(self.mask),
        }


__all__ = ["SignatureEmbedding"]
