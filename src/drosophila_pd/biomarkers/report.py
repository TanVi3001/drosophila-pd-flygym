"""Serialization and self-contained dashboard outputs for biomarkers."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path
from typing import Any

import numpy as np

from .core import BiomarkerReport, BiomarkerValue, calculate_biomarkers


def write_biomarker_report(
    dataset: str | Path | BiomarkerReport,
    output_dir: str | Path,
) -> BiomarkerReport:
    """Calculate, serialize, and dashboard one imported dataset."""

    report = dataset if isinstance(dataset, BiomarkerReport) else calculate_biomarkers(dataset)
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    (root / "biomarkers.json").write_text(
        json.dumps(report.as_dict(), indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    _write_csv(report, root / "biomarkers.csv")
    (root / "biomarkers.md").write_text(_markdown(report), encoding="utf-8")
    (root / "digital_twin_dashboard.html").write_text(_dashboard(report), encoding="utf-8")
    return report


def _write_csv(report: BiomarkerReport, path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("dataset_id", "biomarker", "status", "value", "unit", "formula", "source", "details"),
        )
        writer.writeheader()
        for value in report.biomarkers.values():
            writer.writerow(
                {
                    "dataset_id": report.dataset_id,
                    "biomarker": value.name,
                    "status": "available" if value.available else "unavailable",
                    "value": "" if not value.available else value.value,
                    "unit": value.unit,
                    "formula": value.formula,
                    "source": ";".join(value.source),
                    "details": json.dumps(value.details, separators=(",", ":"), allow_nan=False),
                }
            )


def _markdown(report: BiomarkerReport) -> str:
    payload = report.as_dict()
    lines = [
        "# Biomarker Report",
        "",
        f"- Dataset: `{report.dataset_id}`",
        f"- Sources: `{', '.join(report.source_files) or 'none'}`",
        f"- Available: `{payload['available_count']}/{len(report.biomarkers)}`",
        "",
        "This report contains computational summaries of imported rollout artifacts. "
        "It is not a Parkinson's disease diagnosis, biological severity estimate, "
        "or clinical measure.",
        "",
        "## Biomarkers",
        "",
        "| Biomarker | Status | Value | Unit | Formula |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for value in report.biomarkers.values():
        display = value.value if value.available else "unavailable"
        lines.append(
            f"| `{value.name}` | `{('available' if value.available else 'unavailable')}` | "
            f"`{display}` | `{value.unit}` | `{value.formula}` |"
        )
    lines.extend(["", "## Provenance", ""])
    for name, value in report.biomarkers.items():
        lines.append(f"- `{name}` source: `{', '.join(value.source)}`")
        if not value.available:
            lines.append(f"  reason: {value.details.get('reason', 'missing input')}")
    lines.extend(["", "## Scope", "", payload["scientific_scope"], ""])
    return "\n".join(lines)


def _dashboard(report: BiomarkerReport) -> str:
    values = report.biomarkers
    radar_names = (
        "gait_stability_index",
        "locomotion_efficiency",
        "turning_stability",
        "symmetry_score",
        "trajectory_complexity",
    )
    radar = [(name, float(values[name].value)) for name in radar_names if values[name].available]
    radar_svg = _radar_svg(radar)
    trend_svg = _trend_svg(report.signals.get("time_s"), report.signals.get("heading_angle_rad"))
    trajectory_svg = _trajectory_svg(report.signals.get("trajectory_xy"))
    rows = "".join(
        "<tr>"
        f"<td>{html.escape(value.name)}</td>"
        f"<td class=\"{'available' if value.available else 'unavailable'}\">"
        f"{html.escape(str(value.value))}</td>"
        f"<td>{html.escape(value.unit)}</td>"
        f"<td>{html.escape(value.formula)}</td>"
        "</tr>"
        for value in values.values()
    )
    viewer_link = _viewer_link(report)
    viewer_html = (
        f'<a class="viewer" href="{html.escape(viewer_link)}">Open viewer artifact</a>'
        if viewer_link
        else '<span class="muted">Viewer artifact not present in this dataset</span>'
    )
    scope = html.escape(report.as_dict()["scientific_scope"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Digital Twin Biomarkers - {html.escape(report.dataset_id)}</title>
<style>
:root{{color-scheme:dark;--bg:#0c1117;--panel:#151d27;--line:#2a3745;--text:#e7edf3;--muted:#91a0ae;--accent:#62b5d9;--warn:#e4a45c}}
*{{box-sizing:border-box}} body{{background:var(--bg);color:var(--text);font:14px system-ui,sans-serif;margin:0;padding:24px}}
main{{max-width:1240px;margin:auto}} h1{{margin:0 0 4px}} h2{{font-size:1rem;margin:0 0 12px}} .meta,.muted{{color:var(--muted)}}
.toolbar{{display:flex;justify-content:space-between;gap:12px;align-items:center;margin:18px 0}}
.viewer{{color:var(--accent);text-decoration:none;border:1px solid var(--accent);padding:8px 12px;border-radius:6px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}} section{{background:var(--panel);border:1px solid var(--line);border-radius:7px;padding:16px;margin-bottom:14px}}
svg{{width:100%;height:auto;display:block}} .charts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}}
table{{width:100%;border-collapse:collapse}} th,td{{border-bottom:1px solid var(--line);padding:9px 7px;text-align:left;vertical-align:top}} th{{color:var(--muted);font-weight:500}}
.available{{color:var(--text)}} .unavailable{{color:var(--warn)}} .scope{{border-left:3px solid var(--accent);padding-left:10px;color:var(--muted);line-height:1.5}}
</style></head><body><main>
<h1>Digital Twin Biomarker Dashboard</h1><div class="meta">Dataset: <strong>{html.escape(report.dataset_id)}</strong></div>
<div class="toolbar">{viewer_html}<span class="muted">Imported-artifact analysis only</span></div>
<div class="charts"><section><h2>Biomarker radar</h2>{radar_svg}</section>
<section><h2>Orientation trend</h2>{trend_svg}</section>
<section><h2>Trajectory preview</h2>{trajectory_svg}</section></div>
<section><h2>Biomarker table</h2><table><thead><tr><th>Biomarker</th><th>Value</th><th>Unit</th><th>Formula</th></tr></thead><tbody>{rows}</tbody></table></section>
<section class="scope">{scope}</section>
</main></body></html>
"""


def _radar_svg(items: list[tuple[str, float]]) -> str:
    if not items:
        return '<p class="muted">Radar unavailable: no normalized biomarker values.</p>'
    cx, cy, radius = 180, 135, 100
    points = []
    labels = []
    count = len(items)
    for index, (name, value) in enumerate(items):
        angle = -np.pi / 2 + 2 * np.pi * index / count
        x = cx + radius * np.cos(angle)
        y = cy + radius * np.sin(angle)
        points.append(f"{x:.1f},{y:.1f}")
        labels.append(f'<text x="{cx + (radius + 18) * np.cos(angle):.1f}" y="{cy + (radius + 18) * np.sin(angle):.1f}" text-anchor="middle">{html.escape(name)}</text>')
    return f'<svg viewBox="0 0 360 270" role="img" aria-label="Biomarker radar"><circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="#2a3745"/><polygon points="{" ".join(points)}" fill="#62b5d9" fill-opacity=".28" stroke="#62b5d9" stroke-width="2"/>{"".join(labels)}</svg>'


def _trend_svg(time_s: Any, values: Any) -> str:
    if time_s is None or values is None:
        return '<p class="muted">Trend unavailable: no heading time series.</p>'
    x = np.asarray(time_s, dtype=float).reshape(-1)
    y = np.asarray(values, dtype=float).reshape(-1)
    if x.size < 2 or x.size != y.size or not np.isfinite(x).all() or not np.isfinite(y).all():
        return '<p class="muted">Trend unavailable: insufficient finite samples.</p>'
    return _line_svg(x, y, "heading")


def _trajectory_svg(values: Any) -> str:
    if values is None:
        return '<p class="muted">Trajectory unavailable: no position channel.</p>'
    array = np.asarray(values, dtype=float)
    if array.ndim != 2 or array.shape[0] < 2 or array.shape[1] != 2 or not np.isfinite(array).all():
        return '<p class="muted">Trajectory unavailable: insufficient finite samples.</p>'
    return _line_svg(array[:, 0], array[:, 1], "trajectory")


def _line_svg(x: Any, y: Any, label: str) -> str:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x_span = max(float(np.ptp(x)), 1e-12)
    y_span = max(float(np.ptp(y)), 1e-12)
    points = " ".join(
        f"{25 + 310 * (float(a) - float(np.min(x))) / x_span:.1f},{235 - 205 * (float(b) - float(np.min(y))) / y_span:.1f}"
        for a, b in zip(x, y)
    )
    return f'<svg viewBox="0 0 360 260" role="img" aria-label="{html.escape(label)} trend"><polyline points="{points}" fill="none" stroke="#62b5d9" stroke-width="2"/><line x1="25" y1="235" x2="335" y2="235" stroke="#2a3745"/><line x1="25" y1="30" x2="25" y2="235" stroke="#2a3745"/></svg>'


def _viewer_link(report: BiomarkerReport) -> str | None:
    for candidate in (
        report.dataset_dir / "viewer_bundle" / "index.html",
        report.dataset_dir / "viewer" / "index.html",
        report.dataset_dir / "index.html",
    ):
        if candidate.is_file():
            try:
                return candidate.relative_to(report.dataset_dir).as_posix()
            except ValueError:
                return candidate.name
    return None


__all__ = ["write_biomarker_report"]
