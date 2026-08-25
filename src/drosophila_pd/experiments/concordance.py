"""Phân tích computational concordance giữa literature và campaign đã chạy.

Module này chỉ đọc các artifact hiện có. Nó không tính biological similarity,
không suy diễn Parkinson và không thay đổi simulation, Disease Layer hay
Calibration Engine. Khi campaign chưa có simulation record hoàn tất, module
chỉ ghi trạng thái ``WAITING_SIMULATION`` cùng các bảng rỗng có header.
"""

from __future__ import annotations

import csv
from datetime import UTC, datetime
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

from drosophila_pd.experiments.experimental_campaign import (
    KNOWN_PROXIES,
    METRIC_SOURCES,
)


WAITING_SIMULATION = "WAITING_SIMULATION"
WAITING_INPUT_DATA = "WAITING_INPUT_DATA"
PASS = "PASS"

STRONG = "Strong"
MODERATE = "Moderate"
WEAK = "Weak"
UNKNOWN = "Unknown"
INSUFFICIENT = "Insufficient"

SCIENTIFIC_SCOPE = (
    "Day la computational concordance analysis giua literature evidence va "
    "simulation metrics. Ket qua khong phai biological similarity, khong phai "
    "biological validation, clinical prediction hay drug response."
)

AGREEMENT_FIELDS = (
    "proxy",
    "status",
    "literature_paper_count",
    "quantitative_paper_count",
    "mean_evidence_score",
    "literature_metric_count",
    "simulation_condition_count",
    "simulation_metric_count",
    "comparable_metric_count",
    "concordant_metric_count",
    "discordant_metric_count",
    "reason",
)

PROXY_FIELDS = (
    "proxy",
    "status",
    "literature_paper_count",
    "quantitative_paper_count",
    "mean_evidence_score",
    "literature_metrics",
    "simulation_condition_count",
    "simulation_metrics",
    "comparable_metric_count",
    "concordant_metric_count",
    "discordant_metric_count",
    "reason",
)

METRIC_FIELDS = (
    "proxy",
    "literature_metric",
    "simulation_metric",
    "literature_paper_count",
    "quantitative_paper_count",
    "mean_evidence_score",
    "baseline_mean",
    "candidate_mean",
    "delta_mean",
    "target_value",
    "expected_direction",
    "status",
    "reason",
)

INPUT_FILENAMES = (
    "coverage_report.csv",
    "dependency_matrix.csv",
    "evidence_scores.csv",
    "disease_layer_matrix.csv",
)


def run_concordance_analysis(
    *,
    evidence_dir: str | Path,
    design_dir: str | Path,
    campaign_path: str | Path,
    output_dir: str | Path,
    atlas_path: str | Path | None = None,
    targets_path: str | Path | None = None,
) -> dict[str, Any]:
    """Đọc artifact và ghi toàn bộ báo cáo Concordance Analysis.

    ``campaign_path`` phải trỏ đến ``campaign_data.json`` được tạo sau một
    campaign thực sự. File status waiting hoặc file không tồn tại không được
    coi là simulation output.
    """

    output = Path(output_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    inputs = {
        "evidence_dir": str(Path(evidence_dir).expanduser().resolve()),
        "design_dir": str(Path(design_dir).expanduser().resolve()),
        "campaign": str(Path(campaign_path).expanduser().resolve()),
        "atlas": str(Path(atlas_path).expanduser().resolve()) if atlas_path else None,
        "targets": str(Path(targets_path).expanduser().resolve()) if targets_path else None,
    }

    try:
        literature = _load_literature(
            Path(evidence_dir),
            Path(design_dir),
            atlas_path=Path(atlas_path) if atlas_path else None,
            targets_path=Path(targets_path) if targets_path else None,
        )
    except (OSError, ValueError, csv.Error, json.JSONDecodeError) as error:
        payload = _empty_payload(
            status=WAITING_INPUT_DATA,
            inputs=inputs,
            proxies=list(KNOWN_PROXIES),
            reason=f"Khong doc duoc Evidence/Design artifact: {type(error).__name__}: {error}",
        )
        return _write_outputs(output, payload)

    simulation, simulation_reason = _load_simulation(Path(campaign_path))
    if simulation is None:
        payload = _empty_payload(
            status=WAITING_SIMULATION,
            inputs=inputs,
            proxies=literature["proxies"],
            reason=simulation_reason,
            literature=literature,
        )
        return _write_outputs(output, payload)

    metric_rows = _build_metric_validation(literature, simulation)
    proxy_rows = _build_proxy_validation(literature, simulation, metric_rows)
    agreement_rows = _build_agreement_rows(proxy_rows)
    matrix_rows = _build_matrix_rows(metric_rows, literature["proxies"])
    payload = {
        "schema_version": "1.0",
        "status": PASS,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "scientific_scope": SCIENTIFIC_SCOPE,
        "inputs": inputs,
        "simulation": simulation["summary"],
        "literature": literature["summary"],
        "agreement": agreement_rows,
        "proxy_validation": proxy_rows,
        "metric_validation": metric_rows,
        "concordance_matrix": matrix_rows,
        "scientific_results_generated": True,
        "counts": {
            "proxies": len(agreement_rows),
            "metrics": len(metric_rows),
            "strong": sum(row["status"] == STRONG for row in agreement_rows),
            "moderate": sum(row["status"] == MODERATE for row in agreement_rows),
            "weak": sum(row["status"] == WEAK for row in agreement_rows),
            "unknown": sum(row["status"] == UNKNOWN for row in agreement_rows),
            "insufficient": sum(row["status"] == INSUFFICIENT for row in agreement_rows),
        },
    }
    return _write_outputs(output, payload)


def _load_literature(
    evidence_dir: Path,
    design_dir: Path,
    *,
    atlas_path: Path | None,
    targets_path: Path | None,
) -> dict[str, Any]:
    coverage = _read_csv(evidence_dir / "coverage_report.csv")
    dependencies = _read_csv(evidence_dir / "dependency_matrix.csv")
    scores = _read_csv(evidence_dir / "evidence_scores.csv")
    matrix = _read_csv(evidence_dir / "disease_layer_matrix.csv")
    design = _read_csv(design_dir / "proxy_design.csv", required=False)
    atlas = _load_atlas_summary(atlas_path)
    targets = _read_csv(targets_path, required=False) if targets_path else []

    proxies = list(KNOWN_PROXIES)
    for row in coverage + design:
        proxy = str(row.get("proxy", "")).strip()
        if proxy and proxy not in proxies:
            proxies.append(proxy)
    coverage_by_proxy = {str(row.get("proxy", "")).strip(): row for row in coverage}
    design_by_proxy = {str(row.get("proxy", "")).strip(): row for row in design}
    scores_by_proxy = _scores_by_proxy(scores)
    dependency_by_proxy: dict[str, list[dict[str, str]]] = {proxy: [] for proxy in proxies}
    for row in dependencies:
        proxy = str(row.get("proxy", "")).strip()
        if proxy in dependency_by_proxy:
            dependency_by_proxy[proxy].append(row)
    matrix_by_proxy = _matrix_by_proxy(matrix, proxies)
    target_by_metric = _index_targets(targets)
    unique_paper_ids = {
        str(row.get("paper_id", "")).strip()
        for row in scores
        if str(row.get("paper_id", "")).strip()
    }

    proxy_data: dict[str, dict[str, Any]] = {}
    for proxy in proxies:
        coverage_row = coverage_by_proxy.get(proxy, {})
        proxy_dependencies = dependency_by_proxy.get(proxy, [])
        metric_names = _unique(
            [str(row.get("metric", "")).strip() for row in proxy_dependencies]
            + matrix_by_proxy.get(proxy, [])
        )
        scores_for_proxy = scores_by_proxy.get(proxy, [])
        paper_count = _int(coverage_row.get("paper_count"), default=0)
        quantitative_count = _int(
            coverage_row.get("quantitative_paper_count"), default=0
        )
        mean_score = _mean(
            [_float(row.get("evidence_score")) for row in scores_for_proxy]
        )
        proxy_data[proxy] = {
            "proxy": proxy,
            "paper_count": paper_count,
            "quantitative_count": quantitative_count,
            "mean_score": mean_score,
            "metrics": metric_names,
            "dependencies": proxy_dependencies,
            "design": design_by_proxy.get(proxy, {}),
            "targets": target_by_metric,
        }

    return {
        "proxies": proxies,
        "by_proxy": proxy_data,
        "summary": {
            "proxy_count": len(proxies),
            "paper_count": len(unique_paper_ids),
            "quantitative_paper_count": sum(
                item["quantitative_count"] for item in proxy_data.values()
            ),
            "source": str(evidence_dir.expanduser().resolve()),
            "atlas": atlas,
        },
    }


def _load_atlas_summary(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"status": "NOT_PROVIDED", "record_count": 0}
    if not path.is_file():
        return {"status": "MISSING", "record_count": 0, "path": str(path.resolve())}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("Phenotype Atlas JSON phai la object.")
    records = payload.get("records", [])
    metadata = payload.get("metadata", {})
    if not isinstance(metadata, Mapping):
        metadata = {}
    return {
        "status": metadata.get("status", "AVAILABLE"),
        "record_count": len(records) if isinstance(records, list) else 0,
        "path": str(path.resolve()),
    }


def _load_simulation(path: Path) -> tuple[dict[str, Any] | None, str]:
    if not path.is_file():
        return None, f"Khong tim thay simulation campaign artifact: {path.resolve()}"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return None, f"Simulation artifact khong hop le: {type(error).__name__}: {error}"
    if not isinstance(payload, Mapping):
        return None, "Simulation artifact phai la JSON object."
    baseline = payload.get("baseline", [])
    conditions = payload.get("conditions", [])
    if not isinstance(baseline, list) or not isinstance(conditions, list):
        return None, "Simulation artifact thieu baseline hoac conditions list."
    complete_baseline = [row for row in baseline if _record_complete(row)]
    complete_conditions = [row for row in conditions if _record_complete(row)]
    if not complete_baseline or not complete_conditions:
        return None, "Chua co baseline va condition simulation hoan tat."

    baseline_metrics = _aggregate_metrics(complete_baseline)
    condition_metrics: dict[str, dict[str, list[float]]] = {}
    condition_counts: dict[str, int] = {}
    for record in complete_conditions:
        proxy = str(record.get("proxy", "")).strip()
        if not proxy:
            continue
        condition_counts[proxy] = condition_counts.get(proxy, 0) + 1
        bucket = condition_metrics.setdefault(proxy, {})
        for metric, value in _record_metrics(record).items():
            bucket.setdefault(metric, []).append(value)
    if not condition_metrics:
        return None, "Simulation artifact khong co condition proxy hop le."
    return {
        "baseline": baseline_metrics,
        "conditions": condition_metrics,
        "condition_counts": condition_counts,
        "summary": {
            "baseline_count": len(complete_baseline),
            "condition_count": len(complete_conditions),
            "proxy_count": len(condition_metrics),
            "status_source": payload.get("status"),
        },
    }, ""


def _build_metric_validation(
    literature: Mapping[str, Any], simulation: Mapping[str, Any]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    baseline = simulation["baseline"]
    for proxy in literature["proxies"]:
        data = literature["by_proxy"][proxy]
        for dependency in data["dependencies"]:
            literature_metric = str(dependency.get("metric", "")).strip()
            simulation_metric = _canonical_metric(literature_metric)
            simulation_values = (
                simulation["conditions"].get(proxy, {}).get(simulation_metric, [])
                if simulation_metric
                else []
            )
            baseline_mean = baseline.get(simulation_metric) if simulation_metric else None
            candidate_mean = _mean(simulation_values)
            delta = (
                candidate_mean - baseline_mean
                if candidate_mean is not None and baseline_mean is not None
                else None
            )
            target_value = _target_for_metric(
                literature_metric,
                simulation_metric,
                data["targets"],
                dependency,
            )
            expected_direction = _expected_direction(dependency)
            status, reason = _metric_agreement(
                paper_count=data["paper_count"],
                quantitative_count=data["quantitative_count"],
                dependency=dependency,
                simulation_values=simulation_values,
                baseline_mean=baseline_mean,
                target_value=target_value,
                expected_direction=expected_direction,
            )
            rows.append(
                {
                    "proxy": proxy,
                    "literature_metric": literature_metric,
                    "simulation_metric": simulation_metric or "",
                    "literature_paper_count": data["paper_count"],
                    "quantitative_paper_count": data["quantitative_count"],
                    "mean_evidence_score": _float_or_none(dependency.get("mean_evidence_score")),
                    "baseline_mean": baseline_mean,
                    "candidate_mean": candidate_mean,
                    "delta_mean": delta,
                    "target_value": target_value,
                    "expected_direction": expected_direction or "",
                    "status": status,
                    "reason": reason,
                }
            )
    return rows


def _build_proxy_validation(
    literature: Mapping[str, Any],
    simulation: Mapping[str, Any],
    metric_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    by_proxy: dict[str, list[Mapping[str, Any]]] = {proxy: [] for proxy in literature["proxies"]}
    for row in metric_rows:
        by_proxy.setdefault(str(row["proxy"]), []).append(row)
    for proxy in literature["proxies"]:
        data = literature["by_proxy"][proxy]
        proxy_metrics = simulation["conditions"].get(proxy, {})
        proxy_metric_rows = by_proxy.get(proxy, [])
        status = _aggregate_status(
            proxy_metrics=proxy_metrics,
            paper_count=data["paper_count"],
            metric_rows=proxy_metric_rows,
        )
        rows.append(
            {
                "proxy": proxy,
                "status": status,
                "literature_paper_count": data["paper_count"],
                "quantitative_paper_count": data["quantitative_count"],
                "mean_evidence_score": data["mean_score"],
                "literature_metrics": ";".join(data["metrics"]),
                "simulation_condition_count": simulation["condition_counts"].get(proxy, 0),
                "simulation_metrics": ";".join(sorted(proxy_metrics)),
                "comparable_metric_count": sum(
                    bool(row.get("simulation_metric")) for row in proxy_metric_rows
                ),
                "concordant_metric_count": sum(
                    row["status"] in {STRONG, MODERATE, WEAK} for row in proxy_metric_rows
                ),
                "discordant_metric_count": sum(
                    row["status"] == "Discordant" for row in proxy_metric_rows
                ),
                "reason": _proxy_reason(status, data, proxy_metrics, proxy_metric_rows),
            }
        )
    return rows


def _build_agreement_rows(proxy_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "proxy": row["proxy"],
            "status": row["status"],
            "literature_paper_count": row["literature_paper_count"],
            "quantitative_paper_count": row["quantitative_paper_count"],
            "mean_evidence_score": row["mean_evidence_score"],
            "literature_metric_count": len(
                [item for item in str(row["literature_metrics"]).split(";") if item]
            ),
            "simulation_condition_count": row["simulation_condition_count"],
            "simulation_metric_count": len(
                [item for item in str(row["simulation_metrics"]).split(";") if item]
            ),
            "comparable_metric_count": row["comparable_metric_count"],
            "concordant_metric_count": row["concordant_metric_count"],
            "discordant_metric_count": row["discordant_metric_count"],
            "reason": row["reason"],
        }
        for row in proxy_rows
    ]


def _build_matrix_rows(
    metric_rows: Sequence[Mapping[str, Any]], proxies: Sequence[str]
) -> list[dict[str, Any]]:
    metrics = _unique([str(row["literature_metric"]) for row in metric_rows])
    return [
        {
            "metric": metric,
            **{
                proxy: next(
                    (
                        row["status"]
                        for row in metric_rows
                        if row["literature_metric"] == metric and row["proxy"] == proxy
                    ),
                    "",
                )
                for proxy in proxies
            },
        }
        for metric in metrics
    ]


def _metric_agreement(
    *,
    paper_count: int,
    quantitative_count: int,
    dependency: Mapping[str, str],
    simulation_values: Sequence[float],
    baseline_mean: float | None,
    target_value: float | None,
    expected_direction: str | None,
) -> tuple[str, str]:
    if paper_count == 0:
        return UNKNOWN, "Khong co literature mapping cho proxy nay."
    if not simulation_values or baseline_mean is None:
        return INSUFFICIENT, "Khong co simulation metric tuong ung de so sanh."
    if quantitative_count == 0 and target_value is None:
        return INSUFFICIENT, "Literature chi qualitative hoac chua co numeric target duoc duyet."
    if not expected_direction:
        return INSUFFICIENT, "Chua co expected direction tu literature; khong tu suy dien huong."

    deltas = [value - baseline_mean for value in simulation_values]
    nonzero = [delta for delta in deltas if abs(delta) > 1e-12]
    if not nonzero:
        return INSUFFICIENT, "Simulation khong tao response delta co the danh gia."
    matches = sum(_direction_matches(delta, expected_direction) for delta in nonzero)
    ratio = matches / len(nonzero)
    confidence = _float_or_none(dependency.get("mean_confidence_weight")) or 0.0
    if ratio == 1.0 and quantitative_count > 0 and confidence >= 0.75:
        return STRONG, "Tat ca response delta cung huong voi numeric literature target."
    if ratio >= 0.5 and quantitative_count > 0:
        return MODERATE, "Phan lon response delta cung huong voi numeric literature target."
    if ratio > 0:
        return WEAK, "Chi mot phan response delta cung huong voi literature expectation."
    return "Discordant", "Response delta khong cung huong voi literature expectation."


def _aggregate_status(
    *,
    proxy_metrics: Mapping[str, Sequence[float]],
    paper_count: int,
    metric_rows: Sequence[Mapping[str, Any]],
) -> str:
    if paper_count == 0:
        return UNKNOWN
    if not proxy_metrics:
        return INSUFFICIENT
    statuses = [str(row["status"]) for row in metric_rows]
    if STRONG in statuses:
        return STRONG
    if MODERATE in statuses:
        return MODERATE
    if WEAK in statuses:
        return WEAK
    return INSUFFICIENT


def _proxy_reason(
    status: str,
    literature: Mapping[str, Any],
    simulation_metrics: Mapping[str, Sequence[float]],
    metric_rows: Sequence[Mapping[str, Any]],
) -> str:
    if status == UNKNOWN:
        return "Khong co literature evidence cho proxy."
    if not simulation_metrics:
        return "Co literature mapping nhung chua co simulation response cho proxy."
    if not metric_rows:
        return "Co simulation response nhung khong co metric mapping de doi chieu."
    if all(row["status"] == INSUFFICIENT for row in metric_rows):
        return "Co metric mapping nhung evidence hien tai chua co numeric target/direction."
    return f"Danh gia computational tren {len(metric_rows)} metric mapping; khong phai ket luan sinh hoc."


def _write_outputs(output: Path, payload: dict[str, Any]) -> dict[str, Any]:
    agreement_rows = payload.get("agreement", [])
    proxy_rows = payload.get("proxy_validation", [])
    metric_rows = payload.get("metric_validation", [])
    matrix_rows = payload.get("concordance_matrix", [])
    proxies = [row["proxy"] for row in proxy_rows]
    _write_csv(output / "agreement.csv", AGREEMENT_FIELDS, agreement_rows)
    _write_csv(output / "proxy_validation.csv", PROXY_FIELDS, proxy_rows)
    _write_csv(output / "metric_validation.csv", METRIC_FIELDS, metric_rows)
    _write_csv(
        output / "concordance_matrix.csv",
        ["metric", *(proxies or payload.get("proxies", []))],
        matrix_rows,
    )
    (output / "agreement.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    (output / "agreement.md").write_text(_agreement_markdown(payload), encoding="utf-8")
    (output / "research_findings.md").write_text(_findings_markdown(payload), encoding="utf-8")
    (output / "limitations.md").write_text(_limitations_markdown(payload), encoding="utf-8")
    (output / "future_proxy.md").write_text(_future_proxy_markdown(payload), encoding="utf-8")
    return payload


def _empty_payload(
    *,
    status: str,
    inputs: Mapping[str, Any],
    proxies: Sequence[str],
    reason: str,
    literature: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "status": status,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "scientific_scope": SCIENTIFIC_SCOPE,
        "inputs": dict(inputs),
        "proxies": list(proxies),
        "reason": reason,
        "simulation": {"available": False, "reason": reason},
        "literature": literature["summary"] if literature else {},
        "agreement": [],
        "proxy_validation": [],
        "metric_validation": [],
        "concordance_matrix": [],
        "scientific_results_generated": False,
        "counts": {"proxies": len(proxies), "metrics": 0},
    }


def _agreement_markdown(payload: Mapping[str, Any]) -> str:
    lines = [
        "# Concordance Analysis",
        "",
        f"- Trang thai: `{payload.get('status')}`",
        f"- Pham vi: {payload.get('scientific_scope', SCIENTIFIC_SCOPE)}",
        "",
    ]
    if payload.get("status") != PASS:
        lines.extend([
            f"**Chua co agreement result:** {payload.get('reason', 'Chua du dieu kien.')} ",
            "",
            "Khong tao ket luan computational vi simulation chua san sang hoac input chua day du.",
            "",
        ])
        return "\n".join(lines)
    lines.extend([
        "Agreement duoi day la phan loai computational, khong phai biological similarity.",
        "",
        "| Proxy | Status | Literature papers | Quantitative papers | Comparable metrics | Reason |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ])
    for row in payload.get("agreement", []):
        lines.append(
            f"| `{row['proxy']}` | `{row['status']}` | {row['literature_paper_count']} | "
            f"{row['quantitative_paper_count']} | {row['comparable_metric_count']} | {row['reason']} |"
        )
    return "\n".join(lines) + "\n"


def _findings_markdown(payload: Mapping[str, Any]) -> str:
    lines = [
        "# Research Findings",
        "",
        "Bao cao nay chi tong hop computational concordance; khong khang dinh Parkinson va khong khang dinh gia tri sinh hoc.",
        "",
    ]
    if payload.get("status") != PASS:
        lines.extend([
            f"## Trang thai: `{payload.get('status')}`",
            "",
            f"Chua co research finding tu simulation: {payload.get('reason', 'Chua du dieu kien.')}",
            "",
        ])
        return "\n".join(lines)
    lines.extend(["## Ket qua co the bao cao", ""])
    for row in payload.get("agreement", []):
        if row["status"] in {STRONG, MODERATE, WEAK}:
            lines.append(
                f"- `{row['proxy']}`: `{row['status']}` tren metric mapping da co; day la computational response, khong phai biological concordance."
            )
    if not any(row["status"] in {STRONG, MODERATE, WEAK} for row in payload.get("agreement", [])):
        lines.append("- Chua co proxy nao dat Strong/Moderate/Weak; evidence hoac metric mapping van Insufficient/Unknown.")
    return "\n".join(lines) + "\n"


def _limitations_markdown(payload: Mapping[str, Any]) -> str:
    return "\n".join([
        "# Scientific Limitations",
        "",
        "- Phan tich nay khong tinh biological similarity.",
        "- Literature evidence chi duoc coi la comparable khi metric, unit va expected direction duoc ghi ro.",
        "- Evidence qualitative khong duoc nang cap thanh numeric target.",
        "- Climbing, flight, geotaxis, crawling va walking khong duoc tu dong gop thanh mot metric.",
        "- Simulation response khong chung minh co che neuron, dopamine, gene expression hay clinical phenotype.",
        f"- Trang thai lan chay hien tai: `{payload.get('status')}`.",
        "",
    ])


def _future_proxy_markdown(payload: Mapping[str, Any]) -> str:
    return "\n".join([
        "# Future Proxy Suggestions",
        "",
        "Danh sach nay chi la khoang trong evidence can duoc xem xet trong nghien cuu tiep theo; khong co proxy moi nao duoc implement trong Sprint 7.",
        "",
        "- `delay`: can event timestamp hoac reaction-time assay.",
        "- `fatigue`: can repeated-bout hoac within-session decline data.",
        "- `asymmetry`: can left/right joint, contact hoac trajectory data.",
        "- `freezing`: can operational pause threshold va event annotation.",
        "- `postural_instability`: can orientation variance, COM sway hoac posture distribution.",
        "- `latency`: can tach initiation/response event rieng, khong dung completion time thay the.",
        "",
        f"Trang thai evidence/simulation: `{payload.get('status')}`.",
        "",
    ])


def _read_csv(path: Path | None, *, required: bool = True) -> list[dict[str, str]]:
    if path is None:
        return []
    if not path.is_file():
        if required:
            raise FileNotFoundError(path)
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _write_csv(
    path: Path,
    fieldnames: Sequence[str],
    rows: Sequence[Mapping[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(fieldnames),
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def _scores_by_proxy(rows: Sequence[Mapping[str, str]]) -> dict[str, list[Mapping[str, str]]]:
    result: dict[str, list[Mapping[str, str]]] = {}
    for row in rows:
        for proxy in str(row.get("proxy_names", "")).split(";"):
            proxy = proxy.strip()
            if proxy:
                result.setdefault(proxy, []).append(row)
    return result


def _matrix_by_proxy(rows: Sequence[Mapping[str, str]], proxies: Sequence[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {proxy: [] for proxy in proxies}
    for row in rows:
        metric = str(row.get("metric", "")).strip()
        for proxy in proxies:
            if str(row.get(proxy, "")).strip() and metric:
                result[proxy].append(metric)
    return result


def _index_targets(rows: Sequence[Mapping[str, str]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        metric = _canonical_metric(str(row.get("metric", "")))
        if metric:
            result[metric] = {
                "value": _float_or_none(row.get("literature value", row.get("value"))),
                "unit": row.get("unit", ""),
                "status": row.get("status", ""),
            }
    return result


def _target_for_metric(
    literature_metric: str,
    simulation_metric: str | None,
    targets: Mapping[str, Mapping[str, Any]],
    dependency: Mapping[str, str],
) -> float | None:
    direct = _float_or_none(
        dependency.get("literature_value", dependency.get("value"))
    )
    if direct is not None:
        return direct
    if simulation_metric and simulation_metric in targets:
        target = targets[simulation_metric]
        if str(target.get("status", "")).strip().lower() in {"rejected", "pending"}:
            return None
        return _float_or_none(target.get("value"))
    return _float_or_none(targets.get(_canonical_metric(literature_metric), {}).get("value")) if _canonical_metric(literature_metric) else None


def _expected_direction(row: Mapping[str, str]) -> str | None:
    value = str(
        row.get("expected_direction", row.get("direction", row.get("effect_direction", "")))
    ).strip().lower()
    if value in {"decrease", "decreased", "down", "lower", "reduced", "negative"}:
        return "decrease"
    if value in {"increase", "increased", "up", "higher", "elevated", "positive"}:
        return "increase"
    return None


def _canonical_metric(value: str) -> str | None:
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        **{name: name for name in METRIC_SOURCES},
        "mean_planar_speed_mm_s": "walking_speed",
        "planar_path_length_mm": "path_length",
        "heading_variance_rad2": "heading_variance",
        "speed": "walking_speed",
        "walking": "walking_speed",
        "path_length": "path_length",
        "pause": "pause_fraction",
        "joint_velocity": "joint_velocity",
        "orientation": "orientation_stability",
        "symmetry": "symmetry_index",
    }
    return aliases.get(normalized)


def _record_complete(record: Any) -> bool:
    if not isinstance(record, Mapping):
        return False
    status = str(record.get("status", "")).strip().lower()
    return status in {"completed", "complete", "pass", "passed", "success"}


def _record_metrics(record: Mapping[str, Any]) -> dict[str, float]:
    raw = record.get("metrics", {})
    if not isinstance(raw, Mapping) or not raw:
        raw = record.get("report", {}).get("derived_locomotion_metrics", {})
    if not isinstance(raw, Mapping):
        return {}
    result: dict[str, float] = {}
    for friendly, source in METRIC_SOURCES.items():
        for key in (source, friendly):
            if key:
                value = _float_or_none(raw.get(key))
                if value is not None:
                    result[friendly] = value
                    break
    return result


def _aggregate_metrics(records: Sequence[Mapping[str, Any]]) -> dict[str, float]:
    grouped: dict[str, list[float]] = {}
    for record in records:
        for metric, value in _record_metrics(record).items():
            grouped.setdefault(metric, []).append(value)
    return {metric: float(sum(values) / len(values)) for metric, values in grouped.items()}


def _direction_matches(delta: float, expected: str) -> bool:
    return (expected == "increase" and delta > 0) or (expected == "decrease" and delta < 0)


def _unique(values: Sequence[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def _int(value: Any, *, default: int) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _float(value: Any) -> float:
    parsed = _float_or_none(value)
    return parsed if parsed is not None else 0.0


def _float_or_none(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _mean(values: Sequence[float | None]) -> float | None:
    available = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    return sum(available) / len(available) if available else None


__all__ = [
    "INSUFFICIENT",
    "MODERATE",
    "PASS",
    "SCIENTIFIC_SCOPE",
    "STRONG",
    "UNKNOWN",
    "WAITING_INPUT_DATA",
    "WAITING_SIMULATION",
    "WEAK",
    "run_concordance_analysis",
]
