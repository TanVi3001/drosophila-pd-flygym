"""Local CSV, JSON, and YAML parser for atlas inputs."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping

import yaml

from .models import PHENOTYPE_ATLAS_FIELDS, PhenotypeRecord


def parse_source(path: str | Path) -> tuple[PhenotypeRecord, ...]:
    """Parse one local source file; this function never crawls the internet."""

    source = Path(path)
    suffix = source.suffix.lower()
    if suffix == ".csv":
        return _parse_csv(source)
    if suffix == ".json":
        with source.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return _parse_payload(payload, source)
    if suffix in {".yaml", ".yml"}:
        with source.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or {}
        return _parse_payload(payload, source)
    raise ValueError(f"Unsupported atlas source format: {source.suffix}")


def _parse_csv(source: Path) -> tuple[PhenotypeRecord, ...]:
    with source.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = tuple(reader.fieldnames or ())
        missing = [field for field in PHENOTYPE_ATLAS_FIELDS if field not in fields]
        if missing:
            raise ValueError(f"Atlas CSV is missing required fields: {missing}")
        records = []
        for index, raw in enumerate(reader, start=2):
            values = {field: _parse_scalar(raw.get(field)) for field in PHENOTYPE_ATLAS_FIELDS}
            if not any(value not in (None, "") for value in values.values()):
                continue
            try:
                records.append(PhenotypeRecord.from_mapping(values))
            except ValueError as error:
                raise ValueError(f"Invalid atlas CSV row {index}: {error}") from error
    return tuple(records)


def _parse_payload(payload: Any, source: Path) -> tuple[PhenotypeRecord, ...]:
    if isinstance(payload, Mapping):
        raw_records = payload.get("records", payload.get("phenotypes"))
        if raw_records is None:
            raise ValueError(f"Atlas document {source} requires a records list.")
    elif isinstance(payload, list):
        raw_records = payload
    else:
        raise ValueError(f"Atlas document {source} must contain a records list.")
    if not isinstance(raw_records, list):
        raise ValueError(f"Atlas document {source} records must be a list.")
    records = []
    for index, raw in enumerate(raw_records):
        if not isinstance(raw, Mapping):
            raise ValueError(f"Atlas record {index} must be a mapping.")
        records.append(PhenotypeRecord.from_mapping(raw))
    return tuple(records)


def _parse_scalar(value: Any) -> Any:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return text


__all__ = ["parse_source"]
