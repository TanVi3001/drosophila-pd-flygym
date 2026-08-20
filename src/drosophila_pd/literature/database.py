"""In-memory atlas database assembled from local source files."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable

from .models import PhenotypeRecord
from .parser import parse_source


@dataclass(frozen=True)
class PhenotypeDatabase:
    records: tuple[PhenotypeRecord, ...] = ()
    source_path: str | None = None

    @classmethod
    def from_records(
        cls,
        records: Iterable[PhenotypeRecord],
        *,
        source_path: str | None = None,
    ) -> "PhenotypeDatabase":
        return cls(tuple(records), source_path)

    @classmethod
    def from_path(cls, path: str | Path) -> "PhenotypeDatabase":
        source = Path(path)
        return cls(parse_source(source), str(source.resolve()))

    def to_mapping(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "source_path": self.source_path,
            "records": [record.to_mapping() for record in self.records],
        }

    def write_json(self, path: str | Path) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(self.to_mapping(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return destination


def load_database(path: str | Path) -> PhenotypeDatabase:
    """Load CSV, JSON, or YAML records into the local atlas database."""

    return PhenotypeDatabase.from_path(path)


__all__ = ["PhenotypeDatabase", "load_database"]
