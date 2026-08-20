"""Deterministic report writers for calibration runs."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .calibration_engine import CalibrationRun
from .validation import validate_calibration_run


def write_calibration_reports(run: CalibrationRun, output_dir: str | Path) -> dict[str, Path]:
    """Write JSON, Markdown, ranking, and objective-breakdown artifacts."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    validation = validate_calibration_run(run)
    summary = run.to_mapping()
    summary["validation"] = validation
    summary_path = output / "calibration_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ranking_path = output / "parameter_ranking.csv"
    with ranking_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("rank", "candidate_id", "status", "loss", "parameters"),
        )
        writer.writeheader()
        for rank, candidate in enumerate(run.ranked_candidates, start=1):
            writer.writerow(
                {
                    "rank": rank,
                    "candidate_id": candidate.candidate_id,
                    "status": candidate.objective.status,
                    "loss": candidate.objective.loss,
                    "parameters": json.dumps(candidate.parameters, sort_keys=True),
                }
            )

    breakdown_path = output / "objective_breakdown.csv"
    with breakdown_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "candidate_id",
                "metric",
                "target_id",
                "observed",
                "target",
                "normalized_error",
                "weight",
                "contribution",
            ),
        )
        writer.writeheader()
        for candidate in run.candidates:
            for item in candidate.objective.contributions:
                writer.writerow({"candidate_id": candidate.candidate_id, **item.to_mapping()})

    report_path = output / "calibration_report.md"
    report_path.write_text(_render_markdown(run, validation), encoding="utf-8")
    return {
        "summary": summary_path,
        "report": report_path,
        "ranking": ranking_path,
        "objective_breakdown": breakdown_path,
    }


def _render_markdown(run: CalibrationRun, validation: dict[str, object]) -> str:
    lines = [
        "# Literature-Constrained Computational Phenotype Calibration",
        "",
        "## Scope",
        "",
        "This report scores supplied simulation metrics against supplied literature records.",
        "It does not establish a biological Parkinson model, clinical value, treatment response, or wet-lab equivalence.",
        "",
        "## Summary",
        "",
        f"- Status: `{run.status}`",
        f"- Objective: `{run.objective_method}`",
        f"- Literature records/targets: `{run.target_count}` / `{run.numeric_target_count}` numeric",
        f"- Candidates: `{run.candidate_count}`",
        f"- Best candidate: `{run.best_candidate_id or 'none'}`",
        f"- Structural validation: `{'PASS' if validation['valid'] else 'FAILED'}`",
        "",
        "## Candidate ranking",
        "",
        "| Rank | Candidate | Status | Loss | Parameters |",
        "| ---: | --- | --- | ---: | --- |",
    ]
    for rank, candidate in enumerate(run.ranked_candidates, start=1):
        lines.append(
            f"| {rank} | {candidate.candidate_id} | {candidate.objective.status} | "
            f"{candidate.objective.loss:.8g} | `{candidate.parameters}` |"
        )
    if not run.ranked_candidates:
        lines.append("| - | none | unavailable | - | - |")
    lines.extend(
        [
            "",
            "## Validation boundary",
            "",
            "Missing numeric targets remain unavailable. No value is imputed and no biological interpretation is inferred.",
            "",
        ]
    )
    return "\n".join(lines)


__all__ = ["write_calibration_reports"]
