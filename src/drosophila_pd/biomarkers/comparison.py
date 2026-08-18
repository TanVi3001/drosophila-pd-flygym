"""Comparison tables for computational biomarker reports."""

from __future__ import annotations

from dataclasses import dataclass
import csv
import json
from pathlib import Path
from typing import Any, Sequence

from .core import BiomarkerReport, calculate_biomarkers


@dataclass(frozen=True)
class BiomarkerComparison:
    """A side-by-side comparison without assigning condition meaning."""

    reports: tuple[BiomarkerReport, ...]

    def as_dict(self) -> dict[str, Any]:
        names = tuple(self.reports[0].biomarkers) if self.reports else ()
        return {
            "schema_version": 1,
            "comparison_type": "single_dataset" if len(self.reports) <= 1 else "side_by_side",
            "scientific_scope": (
                "Side-by-side computational biomarker values from imported artifacts; "
                "no biological or disease classification is performed."
            ),
            "datasets": [report.dataset_id for report in self.reports],
            "values": {
                name: {
                    report.dataset_id: report.biomarkers[name].as_dict()
                    for report in self.reports
                    if name in report.biomarkers
                }
                for name in names
            },
        }


def compare_biomarkers(
    datasets: Sequence[str | Path | BiomarkerReport],
    output_dir: str | Path,
) -> BiomarkerComparison:
    """Calculate and write a one- or multi-dataset biomarker comparison."""

    reports = tuple(item if isinstance(item, BiomarkerReport) else calculate_biomarkers(item) for item in datasets)
    comparison = BiomarkerComparison(reports)
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    (root / "comparison.json").write_text(json.dumps(comparison.as_dict(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    _write_csv(comparison, root / "comparison.csv")
    (root / "comparison.md").write_text(_markdown(comparison), encoding="utf-8")
    return comparison


def _write_csv(comparison: BiomarkerComparison, path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("dataset_id", "biomarker", "status", "value", "unit"))
        writer.writeheader()
        for report in comparison.reports:
            for value in report.biomarkers.values():
                writer.writerow(
                    {
                        "dataset_id": report.dataset_id,
                        "biomarker": value.name,
                        "status": "available" if value.available else "unavailable",
                        "value": "" if not value.available else value.value,
                        "unit": value.unit,
                    }
                )


def _markdown(comparison: BiomarkerComparison) -> str:
    lines = [
        "# Biomarker Comparison",
        "",
        f"- Type: `{('single_dataset' if len(comparison.reports) <= 1 else 'side_by_side')}`",
        f"- Datasets: `{', '.join(report.dataset_id for report in comparison.reports) or 'none'}`",
        "",
        "Values are reported side by side using the same computational formulas. "
        "No disease classification or biological interpretation is applied.",
        "",
    ]
    if comparison.reports:
        names = tuple(comparison.reports[0].biomarkers)
        lines.extend(["| Biomarker | " + " | ".join(report.dataset_id for report in comparison.reports) + " |", "| --- | " + " | ".join("---:" for _ in comparison.reports) + " |"])
        for name in names:
            cells = []
            for report in comparison.reports:
                value = report.biomarkers[name]
                cells.append(str(value.value))
            lines.append(f"| `{name}` | " + " | ".join(f"`{cell}`" for cell in cells) + " |")
    else:
        lines.append("No datasets were supplied.")
    return "\n".join(lines) + "\n"


__all__ = ["BiomarkerComparison", "compare_biomarkers"]
