"""Report generation for the Digital Phenotype Atlas."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .database import PhenotypeDatabase
from .knowledge_graph import build_knowledge_graph
from .models import METRIC_FIELDS
from .statistics import build_statistics
from .validation import validate_database


def write_atlas_report(database: PhenotypeDatabase, output_dir: str | Path) -> dict[str, Path]:
    """Write atlas summaries without adding or inferring records."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    statistics = build_statistics(database.records)
    validation = validate_database(database.records)
    graph = build_knowledge_graph(database.records)
    coverage = {**statistics["coverage"], "validation": validation}

    atlas_payload = {
        "schema_version": "1.0",
        "record_count": len(database.records),
        "validation": validation,
        "statistics": statistics,
        "knowledge_graph": graph.to_mapping(),
        "source_path": database.source_path,
        "scientific_scope": (
            "Literature curation and coverage reporting only; no automatic "
            "phenotype or evidence interpretation."
        ),
    }
    paths = {
        "atlas_report": output / "atlas_report.md",
        "atlas_report_json": output / "atlas_report.json",
        "missing_information": output / "missing_information.md",
        "evidence_matrix": output / "evidence_matrix.csv",
        "coverage_report": output / "coverage_report.md",
        "coverage": output / "coverage.json",
        "gene_summary": output / "gene_summary.csv",
        "assay_summary": output / "assay_summary.csv",
        "phenotype_summary": output / "phenotype_summary.csv",
        "quality_distribution": output / "quality_distribution.csv",
    }
    paths["atlas_report_json"].write_text(
        json.dumps(atlas_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths["coverage"].write_text(
        json.dumps(coverage, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths["atlas_report"].write_text(_atlas_markdown(database, validation, statistics, graph), encoding="utf-8")
    paths["coverage_report"].write_text(_coverage_markdown(statistics, validation), encoding="utf-8")
    paths["missing_information"].write_text(_missing_markdown(database, validation), encoding="utf-8")
    _write_rows(paths["gene_summary"], statistics["gene_summary"], ("value", "record_count", "metric_count"))
    _write_rows(paths["assay_summary"], statistics["assay_summary"], ("value", "record_count", "metric_count"))
    _write_rows(paths["phenotype_summary"], statistics["phenotype_summary"], ("metric", "record_count", "available_count", "missing_count"))
    _write_rows(paths["quality_distribution"], statistics["quality_distribution"], ("bucket", "record_count"))
    _write_evidence_matrix(paths["evidence_matrix"], database)
    return paths


def _write_evidence_matrix(path: Path, database: PhenotypeDatabase) -> None:
    fields = ("paper_id", "gene", "assay", "metric", "value", "unit", "figure_reference", "table_reference", "supplementary_reference", "provenance")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in database.records:
            for metric in METRIC_FIELDS:
                value = record.metric_value(metric)
                if value is None:
                    continue
                writer.writerow(
                    {
                        "paper_id": record.paper_id,
                        "gene": record.get("gene"),
                        "assay": record.get("assay"),
                        "metric": metric,
                        "value": value,
                        "unit": record.get("walking_speed_unit") if metric == "walking_speed_mean" else "",
                        "figure_reference": record.get("figure_reference"),
                        "table_reference": record.get("table_reference"),
                        "supplementary_reference": record.get("supplementary_reference"),
                        "provenance": record.provenance_record.to_json(),
                    }
                )


def _write_rows(path: Path, rows: list[dict[str, Any]], fields: tuple[str, ...]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _atlas_markdown(database: PhenotypeDatabase, validation: dict[str, Any], statistics: dict[str, Any], graph: Any) -> str:
    return "\n".join(
        [
            "# Digital Phenotype Atlas Report",
            "",
            "This report describes curated literature records and their coverage. It does not create phenotype data or infer biological value.",
            "",
            f"- Records: `{len(database.records)}`",
            f"- Structural validation: `{'PASS' if validation['valid'] else 'FAILED'}`",
            f"- Graph nodes: `{len(graph.nodes)}`",
            f"- Graph edges: `{len(graph.edges)}`",
            "",
            "## Numeric metric coverage",
            "",
            "| Metric | Available records | Total records |",
            "| --- | ---: | ---: |",
        ]
        + [
            f"| {metric} | {count} | {len(database.records)} |"
            for metric, count in statistics["coverage"]["metric_coverage"].items()
        ]
        + [
            "",
            "## Boundary",
            "",
            "The atlas is a literature knowledge base for later review and calibration. It is not an AI system, disease model, clinical predictor, or substitute for experimental evidence.",
            "",
        ]
    )


def _coverage_markdown(statistics: dict[str, Any], validation: dict[str, Any]) -> str:
    lines = [
        "# Atlas Coverage Report",
        "",
        f"- Records: `{statistics['coverage']['record_count']}`",
        f"- Validation: `{'PASS' if validation['valid'] else 'FAILED'}`",
        "",
        "## Metric coverage",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
    ]
    lines.extend(
        f"| {metric} | {count} |"
        for metric, count in statistics["coverage"]["metric_coverage"].items()
    )
    return "\n".join(lines) + "\n"


def _missing_markdown(database: PhenotypeDatabase, validation: dict[str, Any]) -> str:
    lines = [
        "# Missing Information",
        "",
        "Missing values are reported for curation follow-up. They are not imputed.",
        "",
    ]
    if not database.records:
        lines.append("No records are present in the template.")
    elif validation["issues"]:
        lines.extend(f"- `{item}`" for item in validation["issues"])
    else:
        lines.append("No structural issues were found.")
    return "\n".join(lines) + "\n"


__all__ = ["write_atlas_report"]
