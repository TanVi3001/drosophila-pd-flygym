"""Artifact reports for signature matching."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .matcher import MatchingReport


def write_signature_reports(report: MatchingReport, output_dir: str | Path) -> dict[str, Path]:
    """Write ranking, similarity, distance matrix, and Markdown summary."""

    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary": root / "signature_report.md",
        "similarity": root / "signature_similarity.csv",
        "distance_matrix": root / "signature_distance_matrix.csv",
        "ranking": root / "ranking.json",
    }
    paths["ranking"].write_text(json.dumps(report.to_mapping(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    _write_similarity(report, paths["similarity"])
    _write_distance_matrix(report, paths["distance_matrix"])
    paths["summary"].write_text(_markdown(report), encoding="utf-8")
    return paths


def _write_similarity(report: MatchingReport, path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("rank", "signature_id", "distance", "similarity", "status", "shared_metrics"))
        writer.writeheader()
        for item in report.results:
            writer.writerow(
                {
                    "rank": item.rank or "",
                    "signature_id": item.signature_id,
                    "distance": "" if item.distance.distance is None else item.distance.distance,
                    "similarity": "" if item.similarity is None else item.similarity,
                    "status": item.distance.status,
                    "shared_metrics": ",".join(item.distance.fields),
                }
            )


def _write_distance_matrix(report: MatchingReport, path: Path) -> None:
    fieldnames = ["signature_id", *[item.signature_id for item in report.results]]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        row: dict[str, Any] = {field: "" for field in fieldnames}
        row["signature_id"] = report.literature_id
        for item in report.results:
            row[item.signature_id] = "" if item.distance.distance is None else item.distance.distance
        writer.writerow(row)


def _markdown(report: MatchingReport) -> str:
    lines = [
        "# Disease Signature Matching Report",
        "",
        f"- Literature signature: `{report.literature_id}`",
        f"- Distance: `{report.distance_method}`",
        f"- Normalization: `{report.normalization_method}`",
        f"- Candidates: `{len(report.results)}`",
        "",
        "This report measures computational phenotype concordance only. The similarity score is not a medical probability, disease stage, or biological severity.",
        "",
        "## Ranking",
        "",
        "| Rank | Signature | Distance | Similarity | Status | Shared metrics |",
        "| ---: | --- | ---: | ---: | --- | --- |",
    ]
    for item in report.results:
        lines.append(
            f"| {item.rank or ''} | `{item.signature_id}` | `{_display(item.distance.distance)}` | `{_display(item.similarity)}` | `{item.distance.status}` | `{', '.join(item.distance.fields)}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "The ranking identifies the closest supplied computational signature under the declared normalization and distance method. It does not identify a biological disease state or establish clinical relevance.",
            "",
        ]
    )
    return "\n".join(lines)


def _display(value: Any) -> str:
    return "unavailable" if value is None else str(value)


__all__ = ["write_signature_reports"]
