"""Comparison figures and HTML report for an experiment suite."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Mapping

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt
import numpy as np

from drosophila_pd.analysis import LoadedRollout


COMPARISON_FIGURES = (
    "boxplot",
    "violin_plot",
    "histogram",
    "trajectory_overlay",
    "com_comparison",
    "speed_comparison",
    "orientation_comparison",
    "joint_comparison",
)


def write_comparison_report(
    records: Any,
    rollouts: Mapping[str, LoadedRollout],
    output_dir: str | Path,
) -> dict[str, Any]:
    """Write requested comparison plots from completed imported rollouts."""

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    completed = [record for record in records if record.status == "COMPLETED"]
    files: dict[str, str] = {}
    files["boxplot"] = _scalar_plot(completed, "boxplot", directory / "boxplot.png")
    files["violin_plot"] = _distribution_plot(completed, rollouts, "violin", directory / "violin_plot.png")
    files["histogram"] = _distribution_plot(completed, rollouts, "histogram", directory / "histogram.png")
    files["trajectory_overlay"] = _trajectory_plot(completed, rollouts, directory / "trajectory_overlay.png", "Thorax trajectory overlay", "thorax")
    files["com_comparison"] = _trajectory_plot(completed, rollouts, directory / "com_comparison.png", "COM comparison", "com")
    files["speed_comparison"] = _series_plot(completed, rollouts, directory / "speed_comparison.png", "Speed comparison", "speed")
    files["orientation_comparison"] = _series_plot(completed, rollouts, directory / "orientation_comparison.png", "Orientation comparison", "heading")
    files["joint_comparison"] = _joint_plot(completed, rollouts, directory / "joint_comparison.png")
    return {"files": files, "completed_experiments": [record.experiment_id for record in completed]}


def write_final_report(summary: Mapping[str, Any], comparison: Mapping[str, Any], path: str | Path) -> Path:
    """Write a sortable/filterable HTML report with a Plotly comparison chart."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    records = list(summary.get("experiments", ()))
    metric_names = (
        "walking_speed_mm_s",
        "total_distance_mm",
        "com_velocity_mean_mm_s",
        "heading_variance_rad2",
        "stride_frequency_hz",
        "step_frequency_hz",
        "symmetry_index",
    )
    rows = []
    for record in records:
        values = [record.get("metrics", {}).get(metric) for metric in metric_names]
        rows.append([record.get("experiment_id", ""), record.get("condition", ""), record.get("status", ""), *values])
    columns = ["Experiment", "Condition", "Status", *metric_names]
    table_header = "".join(f"<th>{html.escape(column)}</th>" for column in columns)
    table_rows = "\n".join(
        "<tr>" + "".join(f"<td>{html.escape(_display(value))}</td>" for value in row) + "</tr>"
        for row in rows
    )
    labels = [str(row[0]) for row in rows]
    speeds = [_number(row[3]) for row in rows]
    plot_data = json.dumps([{"x": labels, "y": speeds, "type": "bar", "name": "Walking speed"}], allow_nan=False)
    counts = summary.get("counts", {})
    comparison_links = "\n".join(
        f'<a href="comparison/{html.escape(name)}.png">{html.escape(name)}.png</a>'
        for name in COMPARISON_FIGURES
    )
    target.write_text(
        f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Experiment Suite Report</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
body{{background:#10161d;color:#e7edf2;font:15px system-ui,sans-serif;margin:0;padding:24px}}
main{{max-width:1400px;margin:auto}} h1{{margin:0 0 6px}} .muted{{color:#9eacb8}}
input{{background:#19232d;border:1px solid #40505e;border-radius:5px;color:#fff;padding:9px;width:min(420px,100%)}}
table{{border-collapse:collapse;width:100%;margin-top:14px;background:#19232d}} th,td{{border:1px solid #30404c;padding:8px;text-align:left}} th{{background:#243240;cursor:pointer}}
.table-wrap{{overflow:auto}} .plots{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px}}
.plots a{{color:#8dc7ff;background:#19232d;border:1px solid #30404c;padding:10px;text-decoration:none}}
#speed-chart{{height:360px;background:#19232d;margin:18px 0}}
</style></head><body><main>
<h1>Experiment Suite Report</h1>
<p class="muted">Experiments: {summary.get('experiment_count', 0)} · Completed: {counts.get('COMPLETED', 0)} · Waiting: {counts.get('WAITING_DATASET', 0)} · Failed: {counts.get('FAILED', 0)}</p>
<p>{html.escape(str(summary.get('scientific_scope', '')))}</p>
<input id="filter" type="search" placeholder="Filter experiments..." oninput="filterRows()">
<div class="table-wrap"><table id="metrics-table"><thead><tr>{table_header}</tr></thead><tbody>{table_rows}</tbody></table></div>
<div id="speed-chart"></div>
<h2>Comparison figures</h2><div class="plots">{comparison_links}</div>
<script>
const chartData = {plot_data};
Plotly.newPlot('speed-chart', chartData, {{title:'Walking speed by experiment', paper_bgcolor:'#19232d', plot_bgcolor:'#19232d', font:{{color:'#e7edf2'}}, xaxis:{{title:'Experiment'}}, yaxis:{{title:'Speed (mm/s)'}}}}, {{responsive:true}});
function filterRows() {{ const q=document.getElementById('filter').value.toLowerCase(); document.querySelectorAll('#metrics-table tbody tr').forEach(row => row.style.display=row.innerText.toLowerCase().includes(q)?'':'none'); }}
document.querySelectorAll('#metrics-table th').forEach((header,index)=>header.addEventListener('click',()=>{{const body=document.querySelector('#metrics-table tbody');const rows=[...body.rows];rows.sort((a,b)=>a.cells[index].innerText.localeCompare(b.cells[index].innerText,undefined,{{numeric:true}}));rows.forEach(row=>body.appendChild(row));}}));
</script></main></body></html>
""",
        encoding="utf-8",
    )
    return target


def _scalar_plot(records: list[Any], kind: str, path: Path) -> str:
    fig, ax = _figure("Metric comparison")
    names = [record.experiment_id for record in records]
    values = [float(record.metrics.get("walking_speed_mm_s")) for record in records if _number(record.metrics.get("walking_speed_mm_s")) is not None]
    if values:
        ax.boxplot(values, tick_labels=["walking speed"])
        ax.set_ylabel("mm/s")
    else:
        _notice(ax, "No completed experiment data")
    return _save(fig, path)


def _distribution_plot(records: list[Any], rollouts: Mapping[str, LoadedRollout], kind: str, path: Path) -> str:
    fig, ax = _figure("Speed distribution")
    labelled_values = [
        (record.experiment_id, _speed_series(rollouts[record.experiment_id]))
        for record in records
        if record.experiment_id in rollouts
    ]
    finite_values = [(name, item[np.isfinite(item)]) for name, item in labelled_values if item.size and np.isfinite(item).any()]
    if finite_values:
        values = [item for _, item in finite_values]
        if kind == "violin":
            ax.violinplot(values, showmeans=True)
        else:
            for name, item in finite_values:
                ax.hist(item, bins=12, alpha=0.45, label=name)
            ax.legend(loc="best", fontsize="x-small")
        ax.set_ylabel("Speed (mm/s)")
    else:
        _notice(ax, "No completed experiment data")
    return _save(fig, path)


def _trajectory_plot(records: list[Any], rollouts: Mapping[str, LoadedRollout], path: Path, title: str, channel: str) -> str:
    fig, ax = _figure(title)
    plotted = False
    for record in records:
        rollout = rollouts.get(record.experiment_id)
        positions = rollout.com_positions if rollout is not None and channel == "com" else rollout.thorax_positions if rollout is not None else None
        if positions is not None:
            ax.plot(positions[:, 0], positions[:, 1], label=record.experiment_id)
            plotted = True
    if plotted:
        ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)"); ax.axis("equal"); ax.legend(loc="best", fontsize="x-small")
    else:
        _notice(ax, "Channel unavailable")
    return _save(fig, path)


def _series_plot(records: list[Any], rollouts: Mapping[str, LoadedRollout], path: Path, title: str, channel: str) -> str:
    fig, ax = _figure(title)
    plotted = False
    for record in records:
        rollout = rollouts.get(record.experiment_id)
        if rollout is None:
            continue
        if channel == "speed":
            values = _speed_series(rollout)
        else:
            values = _heading_series(rollout)
        if values.size:
            ax.plot(rollout.time_s[:values.size], values, label=record.experiment_id)
            plotted = True
    if plotted:
        ax.set_xlabel("Time (s)"); ax.legend(loc="best", fontsize="x-small")
    else:
        _notice(ax, "Channel unavailable")
    return _save(fig, path)


def _joint_plot(records: list[Any], rollouts: Mapping[str, LoadedRollout], path: Path) -> str:
    fig, ax = _figure("Joint velocity comparison")
    plotted = False
    for record in records:
        rollout = rollouts.get(record.experiment_id)
        if rollout is None:
            continue
        for name, values in sorted(rollout.joint_velocity.items()):
            ax.plot(rollout.time_s, values, alpha=0.35, linewidth=0.8, label=f"{record.experiment_id}:{name}")
            plotted = True
    if plotted:
        ax.set_xlabel("Time (s)"); ax.set_ylabel("Joint velocity");
    else:
        _notice(ax, "Joint channel unavailable")
    return _save(fig, path)


def _figure(title: str):
    fig, ax = plt.subplots(figsize=(7, 4), constrained_layout=True)
    ax.set_title(title)
    ax.grid(alpha=0.25)
    return fig, ax


def _notice(ax, message: str) -> None:
    ax.text(0.5, 0.5, message, ha="center", va="center", transform=ax.transAxes, color="#6b7780")
    ax.set_xticks([]); ax.set_yticks([])


def _save(fig, path: Path) -> str:
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path.as_posix()


def _display(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if np.isfinite(result) else None


def _speed_series(rollout: LoadedRollout) -> np.ndarray:
    if rollout.thorax_positions.shape[0] < 2:
        return np.zeros(rollout.thorax_positions.shape[0], dtype=float)
    delta = np.diff(rollout.thorax_positions[:, :2], axis=0)
    intervals = np.diff(rollout.time_s)
    intervals = np.where(intervals > 0, intervals, rollout.timestep_s)
    return np.concatenate(([0.0], np.linalg.norm(delta, axis=1) / intervals))


def _heading_series(rollout: LoadedRollout) -> np.ndarray:
    if rollout.orientations_wxyz is None:
        return np.asarray([], dtype=float)
    w, x, y, z = rollout.orientations_wxyz.T
    return np.unwrap(np.arctan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z)))


__all__ = ["COMPARISON_FIGURES", "write_comparison_report", "write_final_report"]
