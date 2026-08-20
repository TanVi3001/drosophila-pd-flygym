"""Deterministic parsers for curator-provided local literature files."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .candidate import CandidatePhenotype


SUPPORTED_SUFFIXES = frozenset({".pdf", ".md", ".markdown", ".txt", ".csv"})


class ParserError(ValueError):
    """Raised when a source cannot be parsed without making assumptions."""


def parse_source(path: str | Path) -> tuple[CandidatePhenotype, ...]:
    """Parse explicit fields from one local PDF, text, Markdown, or CSV file."""

    source = Path(path)
    if not source.is_file():
        raise ParserError(f"Source file does not exist: {source}")
    suffix = source.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ParserError(f"Unsupported literature source type: {suffix or '<none>'}")
    if suffix == ".csv":
        return _parse_csv(source)
    text = _read_text_or_pdf(source, suffix)
    return _parse_explicit_blocks(text, source)


def _parse_csv(source: Path) -> tuple[CandidatePhenotype, ...]:
    with source.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    candidates: list[CandidatePhenotype] = []
    for index, row in enumerate(rows, start=1):
        candidate_id = row.get("candidate_id") or row.get("id") or f"{source.stem}_{index:03d}"
        candidates.append(CandidatePhenotype.from_mapping(row, candidate_id=candidate_id, source_file=str(source.resolve())))
    return tuple(candidates)


def _read_text_or_pdf(source: Path, suffix: str) -> str:
    if suffix != ".pdf":
        return source.read_text(encoding="utf-8")
    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise ParserError("PDF input requires optional dependency 'pypdf'; install it before parsing PDFs.") from error
    try:
        reader = PdfReader(str(source))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as error:  # pypdf exposes several parser-specific exception types.
        raise ParserError(f"Could not extract text from PDF {source}: {error}") from error


def _parse_explicit_blocks(text: str, source: Path) -> tuple[CandidatePhenotype, ...]:
    """Parse blank-line-separated key/value blocks only.

    Free prose is deliberately ignored. A block must contain ``candidate_id``
    or ``id`` before it can become a candidate.
    """

    candidates: list[CandidatePhenotype] = []
    blocks = _split_blocks(text)
    for block_number, block in enumerate(blocks, start=1):
        fields: dict[str, Any] = {}
        explicit_marker = False
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.lower() == "[candidate]":
                explicit_marker = True
                continue
            separator = ":" if ":" in line else "=" if "=" in line else None
            if separator is None:
                continue
            key, value = line.split(separator, 1)
            fields[key.strip()] = value.strip()
        candidate_id = fields.get("candidate_id") or fields.get("id")
        if candidate_id:
            candidates.append(
                CandidatePhenotype.from_mapping(
                    fields,
                    candidate_id=str(candidate_id),
                    source_file=str(source.resolve()),
                )
            )
        elif fields and explicit_marker:
            raise ParserError(f"Explicit candidate block {block_number} is missing candidate_id: {source}")
    return tuple(candidates)


def _split_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if not line.strip() and current:
            blocks.append("\n".join(current))
            current = []
        else:
            current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks


__all__ = ["ParserError", "SUPPORTED_SUFFIXES", "parse_source"]
