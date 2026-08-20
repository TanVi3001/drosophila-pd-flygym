"""Reports for the human review queue."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .candidate import CANDIDATE_FIELDS
from .review import ReviewStatus, ReviewStore
from .validation import validate_candidates


def write_review_reports(store: ReviewStore, output_dir: str | Path) -> dict[str, Path]:
    """Write review summaries and status-specific CSV exports."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary": destination / "review_summary.md",
        "approved": destination / "approved.csv",
        "rejected": destination / "rejected.csv",
        "pending": destination / "pending.csv",
    }
    validation = validate_candidates(store.candidates)
    counts = {status.value: 0 for status in ReviewStatus}
    for candidate in store.candidates:
        counts[store.status_for(candidate.candidate_id).value] += 1
    for name, status in (("approved", ReviewStatus.APPROVED), ("rejected", ReviewStatus.REJECTED), ("pending", ReviewStatus.PENDING)):
        _write_status_csv(paths[name], store, status)
    paths["summary"].write_text(_summary_markdown(store, counts, validation), encoding="utf-8")
    return paths


def _write_status_csv(path: Path, store: ReviewStore, status: ReviewStatus) -> None:
    fields = [*CANDIDATE_FIELDS, "review_status", "reviewer", "reviewed_at", "review_comment"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for candidate in store.candidates:
            entry = store.review_entry(candidate.candidate_id)
            if entry.status is not status:
                continue
            row = candidate.to_mapping()
            row.update(
                {
                    "review_status": entry.status.value,
                    "reviewer": entry.reviewer,
                    "reviewed_at": entry.reviewed_at,
                    "review_comment": entry.comment,
                }
            )
            writer.writerow(row)


def _summary_markdown(store: ReviewStore, counts: dict[str, int], validation: dict[str, Any]) -> str:
    lines = [
        "# Literature review summary",
        "",
        "This report describes curator review state. It is not an automatic scientific conclusion.",
        "",
        "## Queue",
        "",
        f"- Candidates: {len(store.candidates)}",
        f"- Pending: {counts['pending']}",
        f"- Approved: {counts['approved']}",
        f"- Rejected: {counts['rejected']}",
        f"- Validation status: {'PASS' if validation['valid'] else 'ISSUES FOUND'}",
        "",
        "## Validation issues",
        "",
    ]
    if not validation["issues"]:
        lines.append("No validation issues were found in the current candidate set.")
    else:
        lines.extend(f"- `{issue['candidate_id']}` `{issue['code']}`: {issue['message']}" for issue in validation["issues"])
    lines.extend(
        [
            "",
            "Approved candidates are eligible for explicit export to the existing PhenotypeRecord model.",
            "Pending and rejected candidates are never exported by this workflow.",
            "",
        ]
    )
    return "\n".join(lines)


__all__ = ["write_review_reports"]
