"""Evidence Engine orchestration and report serialization."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping

from .coverage import compute_coverage
from .importance import rank_proxy_importance
from .matrix import build_matrices
from .models import EvidenceBundle, EvidenceScore, PaperEvidence, ScoringConfig
from .scoring import load_scoring_config, score_papers
from .validation import load_evidence_inputs


OUTPUT_FILENAMES = (
    "evidence_scores.csv",
    "evidence_scores.json",
    "coverage_report.csv",
    "parameter_importance.csv",
    "dependency_matrix.csv",
    "disease_layer_matrix.csv",
    "research_gap.md",
    "evidence_summary.md",
)


def build_evidence_bundle(
    mapping_csv: str | Path,
    paper_information_json: str | Path,
    candidate_review_csv: str | Path,
    scoring_config: str | Path | Mapping[str, Any] | ScoringConfig | None = None,
) -> EvidenceBundle:
    """Build all Evidence Engine results without writing files."""

    config = load_scoring_config(scoring_config)
    papers = load_evidence_inputs(
        mapping_csv=mapping_csv,
        paper_information_json=paper_information_json,
        candidate_review_csv=candidate_review_csv,
        config=config,
    )
    scores = score_papers(papers, config)
    coverage = compute_coverage(papers, scores, config)
    importance = rank_proxy_importance(papers, scores, coverage, config)
    dependencies, matrix = build_matrices(papers, scores, config.expected_proxies)
    return EvidenceBundle(
        papers=tuple(papers),
        scores=tuple(scores),
        coverage=tuple(coverage),
        importance=tuple(importance),
        dependencies=tuple(dependencies),
        matrix=tuple(matrix),
        config=config,
        input_paths={
            "mapping_csv": str(Path(mapping_csv)),
            "paper_information_json": str(Path(paper_information_json)),
            "candidate_review_csv": str(Path(candidate_review_csv)),
        },
    )


def write_evidence_reports(bundle: EvidenceBundle, output_dir: str | Path) -> dict[str, Path]:
    """Write the requested CSV, JSON and Markdown Evidence Engine outputs."""

    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    paths = {name: root / name for name in OUTPUT_FILENAMES}
    _write_scores_csv(paths["evidence_scores.csv"], bundle.scores, bundle.config)
    paths["evidence_scores.json"].write_text(
        json.dumps(bundle.as_dict(), indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    _write_dataclass_csv(
        paths["coverage_report.csv"],
        [row.as_dict() for row in bundle.coverage],
        ("proxy", "paper_count", "mapping_record_count", "quantitative_paper_count", "qualitative_paper_count", "calibration_candidate_count", "validation_candidate_count", "coverage_status"),
    )
    _write_dataclass_csv(
        paths["parameter_importance.csv"],
        [row.as_dict() for row in bundle.importance],
        ("rank", "proxy", "paper_count", "total_evidence_score", "mean_evidence_score", "quantitative_paper_count", "coverage_status"),
    )
    _write_dataclass_csv(
        paths["dependency_matrix.csv"],
        [row.as_dict() for row in bundle.dependencies],
        ("metric", "proxy", "paper_count", "mapping_record_count", "mean_confidence", "mean_confidence_weight", "mean_evidence_score", "quantitative_paper_count"),
    )
    _write_matrix_csv(paths["disease_layer_matrix.csv"], bundle.matrix, bundle.config.expected_proxies)
    paths["research_gap.md"].write_text(_research_gap_markdown(bundle), encoding="utf-8")
    paths["evidence_summary.md"].write_text(_summary_markdown(bundle), encoding="utf-8")
    return paths


def run_evidence_engine(
    mapping_csv: str | Path,
    paper_information_json: str | Path,
    candidate_review_csv: str | Path,
    output_dir: str | Path,
    scoring_config: str | Path | Mapping[str, Any] | ScoringConfig | None = None,
) -> dict[str, Path]:
    """Load curation artifacts, derive evidence reports and write all outputs."""

    bundle = build_evidence_bundle(
        mapping_csv=mapping_csv,
        paper_information_json=paper_information_json,
        candidate_review_csv=candidate_review_csv,
        scoring_config=scoring_config,
    )
    return write_evidence_reports(bundle, output_dir)


def _write_scores_csv(path: Path, scores: tuple[EvidenceScore, ...], config: ScoringConfig) -> None:
    criteria_names = [criterion.name for criterion in config.criteria]
    fields = [
        "paper_id",
        "evidence_score",
        "evidence_level",
        *criteria_names,
        "quantitative_metric",
        "protocol_available",
        "sample_size_available",
        "calibration_candidate",
        "validation_candidate",
        "proxy_names",
        "mapping_count",
        "manual_review_required",
        "notes",
    ]
    rows = []
    for score in scores:
        rows.append(
            {
                "paper_id": score.paper_id,
                "evidence_score": score.score,
                "evidence_level": score.level,
                **{name: score.criteria.get(name, 0.0) for name in criteria_names},
                "quantitative_metric": score.quantitative_metric,
                "protocol_available": score.protocol_available,
                "sample_size_available": score.sample_size_available,
                "calibration_candidate": score.calibration_candidate,
                "validation_candidate": score.validation_candidate,
                "proxy_names": ";".join(score.proxy_names),
                "mapping_count": score.mapping_count,
                "manual_review_required": score.manual_review_required,
                "notes": "; ".join(score.notes),
            }
        )
    _write_csv(path, fields, rows)


def _write_dataclass_csv(path: Path, rows: list[dict[str, Any]], fieldnames: tuple[str, ...]) -> None:
    fields = list(fieldnames)
    _write_csv(path, fields, rows)


def _write_matrix_csv(path: Path, rows: tuple[Mapping[str, Any], ...], proxies: tuple[str, ...]) -> None:
    fields = ["metric", *proxies]
    _write_csv(path, fields, [dict(row) for row in rows])


def _write_csv(path: Path, fieldnames: list[str], rows: list[Mapping[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _summary_markdown(bundle: EvidenceBundle) -> str:
    scores = bundle.scores
    quantitative = sum(score.quantitative_metric for score in scores)
    calibration = sum(score.calibration_candidate for score in scores)
    validation = sum(score.validation_candidate for score in scores)
    lines = [
        "# Evidence Engine summary",
        "",
        "This report scores literature evidence completeness and provenance only. "
        "It does not run simulation, infer biology, classify disease, or calibrate parameters.",
        "",
        f"- Papers assessed: `{len(scores)}`",
        f"- Papers with a verified quantitative phenotype value: `{quantitative}`",
        f"- Papers marked calibration candidate/conditional: `{calibration}`",
        f"- Papers marked validation candidate/conditional: `{validation}`",
        f"- Total scoring weight: `{bundle.config.total_weight:g}`",
        "",
        "## Evidence scores",
        "",
        "| Paper | Score | Level | Quantitative | Calibration candidate | Validation candidate | Manual review |",
        "| --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for score in scores:
        lines.append(
            f"| `{score.paper_id}` | {score.score:.2f} | {score.level} | "
            f"{score.quantitative_metric} | {score.calibration_candidate} | "
            f"{score.validation_candidate} | {score.manual_review_required} |"
        )
    lines.extend([
        "",
        "## Proxy coverage",
        "",
        "| Proxy | Papers | Quantitative | Qualitative | Calibration candidates | Validation candidates | Status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ])
    for row in bundle.coverage:
        lines.append(
            f"| `{row.proxy}` | {row.paper_count} | {row.quantitative_paper_count} | "
            f"{row.qualitative_paper_count} | {row.calibration_candidate_count} | "
            f"{row.validation_candidate_count} | `{row.coverage_status}` |"
        )
    lines.extend([
        "",
        "## Interpretation boundary",
        "",
        "A high evidence score means that the supplied curation record contains more of the configured provenance and protocol fields. It does not mean that a proxy is biologically important, clinically valid, or ready for calibration.",
        "",
        "See `research_gap.md` for missing evidence and required manual review.",
        "",
    ])
    return "\n".join(lines)


def _research_gap_markdown(bundle: EvidenceBundle) -> str:
    lines = [
        "# Research gaps from the Evidence Engine",
        "",
        "This gap report describes missing or incomplete literature evidence in the supplied curation artifacts. It does not infer biological mechanisms and does not create calibration targets.",
        "",
        "## Proxy coverage gaps",
        "",
        "| Proxy | Paper count | Quantitative papers | Calibration candidates | Validation candidates | Gap |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in bundle.coverage:
        if row.paper_count == 0:
            gap = "No mapped paper in the supplied curation set."
        elif row.quantitative_paper_count == 0:
            gap = "Mapped evidence is qualitative or numeric outcome values are still pending manual extraction."
        elif row.calibration_candidate_count == 0:
            gap = "No calibration candidate is marked in the mapping."
        elif row.validation_candidate_count == 0:
            gap = "No validation candidate is marked in the mapping."
        else:
            gap = "Coverage exists; verify source data and approval state."
        lines.append(
            f"| `{row.proxy}` | {row.paper_count} | {row.quantitative_paper_count} | "
            f"{row.calibration_candidate_count} | {row.validation_candidate_count} | {gap} |"
        )
    lines.extend([
        "",
        "## Required curation work",
        "",
        "- Verify DOI/PMID, genotype, control, assay, age, sex, temperature and sample unit.",
        "- Extract numeric outcomes only from article text, tables or verified source data.",
        "- Keep climbing, flight, crawling, geotaxis and continuous walking as separate metrics until harmonization is approved.",
        "- Review mappings with `manual_review_required=true` before calibration.",
        "- Select calibration and holdout evidence only after the target units and uncertainty are compatible.",
        "- Treat empty matrix cells as missing evidence, not as zero biological effect.",
        "",
        "## Boundary",
        "",
        "This report does not state that any proxy is a diagnosis, a biological neuron model, or a clinically validated biomarker.",
        "",
    ])
    return "\n".join(lines)


__all__ = [
    "OUTPUT_FILENAMES",
    "build_evidence_bundle",
    "run_evidence_engine",
    "write_evidence_reports",
]
