"""Report, figure, CSV, and dashboard outputs for rollout analysis."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt
import numpy as np

from .rollout_analysis import AnalysisResult, LoadedRollout


FIGURE_NAMES = (
    "speed",
    "trajectory",
    "orientation",
    "joint_velocity",
    "joint_acceleration",
    "contact_ratio",
    "comparison",
)


def write_analysis_report(
    metrics: dict[str, Any],
    rollout: LoadedRollout,
    output_dir: str | Path,
) -> AnalysisResult:
    """Write all requested analysis artifacts and return their paths."""

    root = Path(output_dir)
    figures_dir = root / "figures"
    metrics_dir = root / "metrics"
    report_dir = root / "report"
    for directory in (figures_dir, metrics_dir, report_dir):
        directory.mkdir(parents=True, exist_ok=True)

    files: dict[str, Path] = {}
    metrics_path = metrics_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    files["metrics_json"] = metrics_path

    csv_path = metrics_dir / "metrics.csv"
    _write_metrics_csv(metrics, csv_path)
    files["metrics_csv"] = csv_path

    for name, path in _write_figures(metrics, rollout, figures_dir).items():
        files[f"figure_{name}"] = path

    summary_path = report_dir / "summary.md"
    summary_path.write_text(_summary_markdown(metrics, files), encoding="utf-8")
    files["summary"] = summary_path

    dashboard_path = report_dir / "dashboard.html"
    dashboard_path.write_text(_dashboard_html(metrics, files), encoding="utf-8")
    files["dashboard"] = dashboard_path
    return AnalysisResult(metrics=metrics, output_dir=root, files=files)


def _write_metrics_csv(metrics: dict[str, Any], path: Path) -> None:
    rows: list[dict[str, str]] = []
    for key, value in metrics.get("scalar_metrics", {}).items():
        rows.append({"metric": key, "value": _csv_value(value)})
    for group in ("contact_ratio", "contact_duration_s", "joint_rms_velocity", "joint_rms_acceleration", "symmetry_index_by_pair"):
        value = metrics.get(group)
        if isinstance(value, dict):
            for name, item in value.items():
                rows.append({"metric": f"{group}.{name}", "value": _csv_value(item)})
    rows.extend(
        [
            {"metric": "dataset_id", "value": str(metrics.get("dataset_id", ""))},
            {"metric": "frame_count", "value": str(metrics.get("frame_count", ""))},
            {"metric": "duration_s", "value": _csv_value(metrics.get("duration_s"))},
            {"metric": "timestep_s", "value": _csv_value(metrics.get("timestep_s"))},
        ]
    )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("metric", "value"))
        writer.writeheader()
        writer.writerows(rows)


def _write_figures(metrics: dict[str, Any], rollout: LoadedRollout, directory: Path) -> dict[str, Path]:
    time_s = rollout.time_s
    series = metrics.get("timeseries", {})
    files: dict[str, Path] = {}

    fig, ax = _figure("Walking speed")
    _plot_or_notice(ax, time_s, series.get("instantaneous_speed_mm_s"), "Speed (mm/s)", "No speed samples")
    ax.set_xlabel("Time (s)")
    files["speed"] = _save(fig, directory / "speed.png")

    fig, ax = _figure("Trajectory")
    positions = rollout.thorax_positions
    ax.plot(positions[:, 0], positions[:, 1], label="Thorax", linewidth=1.8)
    if rollout.com_positions is not None:
        ax.plot(rollout.com_positions[:, 0], rollout.com_positions[:, 1], label="COM", linewidth=1.4)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.axis("equal")
    ax.legend(loc="best")
    files["trajectory"] = _save(fig, directory / "trajectory.png")

    fig, ax = _figure("Body orientation")
    orientation = metrics.get("body_orientation_variance")
    if isinstance(orientation, dict):
        for key, label in (("roll_rad", "Roll"), ("pitch_rad", "Pitch"), ("yaw_rad", "Yaw")):
            if orientation.get(key) is not None:
                ax.plot(time_s, orientation[key], label=label)
        ax.legend(loc="best")
    else:
        _notice(ax, "Orientation channel unavailable")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Angle (rad)")
    files["orientation"] = _save(fig, directory / "orientation.png")

    files["joint_velocity"] = _joint_figure(rollout.joint_velocity, time_s, directory / "joint_velocity.png", "Joint velocity", "Velocity")
    files["joint_acceleration"] = _joint_figure(rollout.joint_acceleration, time_s, directory / "joint_acceleration.png", "Joint acceleration", "Acceleration")

    fig, ax = _figure("Contact ratio")
    ratios = metrics.get("contact_ratio")
    if isinstance(ratios, dict) and ratios:
        ax.bar(list(ratios), list(ratios.values()), color="#3c8dbc")
        ax.set_ylim(0, 1)
        ax.set_ylabel("Active fraction")
        ax.tick_params(axis="x", rotation=35)
    else:
        _notice(ax, "Contact channel unavailable")
    files["contact_ratio"] = _save(fig, directory / "contact_ratio.png")

    fig, ax = _figure("Trajectory comparison")
    if rollout.com_positions is not None:
        ax.plot(rollout.thorax_positions[:, 0], rollout.thorax_positions[:, 1], label="Thorax")
        ax.plot(rollout.com_positions[:, 0], rollout.com_positions[:, 1], label="COM")
        ax.legend(loc="best")
        ax.set_xlabel("X (mm)")
        ax.set_ylabel("Y (mm)")
        ax.axis("equal")
    else:
        ax.plot(time_s, rollout.thorax_positions[:, 0], label="Thorax X")
        ax.plot(time_s, rollout.thorax_positions[:, 1], label="Thorax Y")
        ax.legend(loc="best")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Position (mm)")
    files["comparison"] = _save(fig, directory / "comparison.png")
    return files


def _joint_figure(
    values: dict[str, np.ndarray],
    time_s: np.ndarray,
    path: Path,
    title: str,
    ylabel: str,
) -> Path:
    fig, ax = _figure(title)
    if values:
        for name, array in sorted(values.items()):
            ax.plot(time_s, array, linewidth=0.9, label=name)
        if len(values) <= 12:
            ax.legend(loc="best", fontsize="x-small")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(ylabel)
    else:
        _notice(ax, "Joint channel unavailable")
    return _save(fig, path)


def _summary_markdown(metrics: dict[str, Any], files: dict[str, Path]) -> str:
    lines = [
        "# Rollout Analysis Summary",
        "",
        f"- Dataset: `{metrics.get('dataset_id', 'unknown')}`",
        f"- Frames: `{metrics.get('frame_count', 0)}`",
        f"- Duration (s): `{metrics.get('duration_s', 0.0):.6g}`",
        f"- Timestep (s): `{metrics.get('timestep_s', 0.0):.6g}`",
        f"- Timestamp reconstruction: `{metrics.get('timestamps_reconstructed', False)}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.get("scalar_metrics", {}).items():
        lines.append(f"| `{key}` | `{_csv_value(value)}` |")
    lines.extend(["", "## Channel availability", ""])
    for key, value in metrics.get("available_channels", {}).items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Figures", ""])
    for name in FIGURE_NAMES:
        path = files.get(f"figure_{name}")
        if path:
            lines.append(f"- [{name}.png](../figures/{name}.png)")
    lines.extend(
        [
            "",
            "## Scope",
            "",
            "These outputs are computational summaries of imported rollout data. "
            "They do not establish biological validity, clinical diagnosis, or a Parkinson's disease mechanism.",
            "",
        ]
    )
    return "\n".join(lines)


def _dashboard_html(metrics: dict[str, Any], files: dict[str, Path]) -> str:
    cards = []
    for key, value in metrics.get("scalar_metrics", {}).items():
        cards.append(f"<article><h3>{html.escape(key)}</h3><p>{html.escape(_csv_value(value))}</p></article>")
    figures = "\n".join(
        f'<figure><img src="../figures/{name}.png" alt="{html.escape(name)}"><figcaption>{html.escape(name)}</figcaption></figure>'
        for name in FIGURE_NAMES
        if f"figure_{name}" in files
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rollout Analysis - {html.escape(str(metrics.get('dataset_id', 'unknown')))}</title>
<style>
body{{background:#10161d;color:#e7edf2;font:15px system-ui,sans-serif;margin:0;padding:24px}}
main{{max-width:1200px;margin:auto}} h1{{margin-top:0}} .meta{{color:#9eacb8}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px}}
article,figure{{background:#19232d;border:1px solid #2d3b48;border-radius:8px;padding:12px}}
article h3{{font-size:.8rem;color:#9eacb8;margin:0 0 8px}} article p{{font-size:1.2rem;margin:0}}
.figures{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}} figure{{margin:0}} img{{width:100%;display:block}} figcaption{{color:#9eacb8;margin-top:8px}}
.scope{{border-left:3px solid #6aa9d6;padding-left:12px;color:#b8c5cf}}
</style></head><body><main>
<h1>Rollout Analysis</h1><p class="meta">Dataset: <strong>{html.escape(str(metrics.get('dataset_id', 'unknown')))}</strong> · Frames: {metrics.get('frame_count', 0)} · Duration: {metrics.get('duration_s', 0.0):.4g}s</p>
<section class="cards">{''.join(cards)}</section>
<h2>Figures</h2><section class="figures">{figures}</section>
<p class="scope">{html.escape(str(metrics.get('scientific_scope', '')))}</p>
</main></body></html>
"""


def _figure(title: str):
    fig, ax = plt.subplots(figsize=(7, 4), constrained_layout=True)
    ax.set_title(title)
    ax.grid(alpha=0.25)
    return fig, ax


def _plot_or_notice(ax, time_s: np.ndarray, values: Any, ylabel: str, message: str) -> None:
    if values is None:
        _notice(ax, message)
    else:
        ax.plot(time_s, values, color="#3c8dbc", linewidth=1.4)
        ax.set_ylabel(ylabel)


def _notice(ax, message: str) -> None:
    ax.text(0.5, 0.5, message, ha="center", va="center", transform=ax.transAxes, color="#6b7780")
    ax.set_xticks([])
    ax.set_yticks([])


def _save(fig, path: Path) -> Path:
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def _csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, separators=(",", ":"), allow_nan=False)
    return str(value)


__all__ = ["FIGURE_NAMES", "write_analysis_report"]
