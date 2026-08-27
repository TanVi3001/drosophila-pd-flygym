"""Điều phối Experimental Campaign v1 bằng các API hiện có.

Module này chỉ làm orchestration, gom metric và ghi báo cáo. Nó không tạo
simulation engine, không mở rộng Disease Layer và không suy diễn sinh học.
"""

from __future__ import annotations

import csv
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
import json
import math
from pathlib import Path
import re
from typing import Any, Callable, Mapping, Sequence

import yaml

from drosophila_pd.experiments.calibration_experiment import RuntimeGate, build_runtime_gate
from drosophila_pd.experiments.healthy_baseline import (
    HealthyBaselineConfig,
    load_healthy_baseline_config,
    run_locomotion,
)
from drosophila_pd.parkinson import DiseaseLayer


WAITING_RUNTIME = "WAITING_RUNTIME"
WAITING_TARGET_DATA = "WAITING_TARGET_DATA"
FAILED_CONFIG = "FAILED_CONFIG"
FAILED = "FAILED"
PASS = "PASS"

SCIENTIFIC_SCOPE = (
    "Đây là computational locomotion experiment. Kết quả mô tả response của "
    "simulation đối với control-level proxy; không phải biological validation, "
    "clinical prediction hoặc drug response."
)

KNOWN_PROXIES = (
    "motor_vigor",
    "coordination",
    "noise",
    "delay",
    "fatigue",
    "latency",
    "freezing",
    "asymmetry",
    "postural_instability",
)

SUPPORTED_PARAMETER_FIELDS = {
    "motor_vigor": "motor_vigor",
    "coordination": "coordination",
    "noise": "motor_noise_std",
    "delay": "initiation_delay_steps",
    "fatigue": "fatigue_rate",
    "latency": "action_latency_steps",
    "freezing": "freezing_probability",
    "asymmetry": "asymmetry",
}

UNSUPPORTED_PROXY_REASONS = {
    "postural_instability": "DiseaseLayer hiện tại không có parameter posture/orientation.",
}

METRIC_SOURCES = {
    "walking_speed": "mean_planar_speed_mm_s",
    "path_length": "planar_path_length_mm",
    "com_displacement": None,
    "heading_variance": "heading_variance_rad2",
    "trajectory_efficiency": "trajectory_efficiency",
    "pause_fraction": "pause_fraction",
    "joint_velocity": "joint_velocity",
    "orientation_stability": "orientation_stability",
    "symmetry_index": "symmetry_index",
}

ConditionRunner = Callable[[HealthyBaselineConfig, DiseaseLayer | None, str], dict[str, Any]]


@dataclass(frozen=True)
class ProxySweep:
    """Một cấu hình sweep cho một proxy đã biết."""

    proxy: str
    enabled: bool
    parameter: str | None
    values: tuple[float, ...]
    left_joint_indices: tuple[int, ...] = ()
    right_joint_indices: tuple[int, ...] = ()
    freezing_duration_steps: int = 0
    reason: str | None = None

    def validate(self) -> None:
        if self.proxy not in KNOWN_PROXIES:
            raise ValueError(f"Proxy không được hỗ trợ: {self.proxy}")
        if not self.enabled:
            return
        if self.proxy in UNSUPPORTED_PROXY_REASONS:
            raise ValueError(f"{self.proxy}: {UNSUPPORTED_PROXY_REASONS[self.proxy]}")
        expected = SUPPORTED_PARAMETER_FIELDS[self.proxy]
        if self.parameter != expected:
            raise ValueError(
                f"Proxy {self.proxy} phải dùng parameter {expected!r}, không phải {self.parameter!r}."
            )
        if not self.values:
            raise ValueError(f"Proxy {self.proxy} cần ít nhất một parameter value.")
        if any(not math.isfinite(value) for value in self.values):
            raise ValueError(f"Proxy {self.proxy} chứa parameter value không finite.")
        if self.proxy == "freezing" and self.freezing_duration_steps <= 0:
            raise ValueError(
                "Freezing sweep cần freezing_duration_steps dương để tạo các pause episode."
            )
        if self.proxy == "asymmetry" and any(value != 0 for value in self.values):
            if not self.left_joint_indices or not self.right_joint_indices:
                raise ValueError(
                    "Asymmetry khác 0 cần left_joint_indices và right_joint_indices đã được xác minh."
                )

    def layer(self, value: float, seed: int, condition_id: str) -> DiseaseLayer:
        self.validate()
        parameters: dict[str, Any] = {
            "name": condition_id,
            "config_id": condition_id,
            "random_seed": seed,
            self.parameter or "motor_vigor": value,
        }
        if self.proxy == "asymmetry":
            parameters["left_joint_indices"] = self.left_joint_indices
            parameters["right_joint_indices"] = self.right_joint_indices
        if self.proxy == "freezing":
            parameters["freezing_duration_steps"] = self.freezing_duration_steps
        return DiseaseLayer.from_mapping(parameters)


@dataclass(frozen=True)
class CampaignConfig:
    """Cấu hình đã validate của Experimental Campaign v1."""

    campaign_name: str
    random_seeds: tuple[int, ...]
    steps: int
    duration_s: float
    output_directory: str
    proxies: tuple[ProxySweep, ...]
    scientific_scope: str

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "CampaignConfig":
        name = str(data.get("campaign_name", data.get("experiment_name", ""))).strip()
        if not name:
            raise ValueError("campaign_name phải là chuỗi không rỗng.")
        raw_seeds = data.get("random_seeds")
        if not isinstance(raw_seeds, list) or not raw_seeds:
            raise ValueError("random_seeds phải là list không rỗng.")
        seeds = tuple(int(seed) for seed in raw_seeds)
        if any(seed < 0 for seed in seeds):
            raise ValueError("random_seeds không được âm.")
        steps = int(data.get("steps", 0))
        duration_s = float(data.get("duration_s", data.get("duration", 0)))
        if steps <= 0 or not math.isfinite(duration_s) or duration_s <= 0:
            raise ValueError("steps phải dương và duration_s phải finite, dương.")
        output_directory = str(data.get("output_directory", "results/experimental_campaign"))
        raw_proxies = data.get("proxies", {})
        if not isinstance(raw_proxies, Mapping):
            raise ValueError("proxies phải là mapping.")
        unknown = sorted(set(raw_proxies) - set(KNOWN_PROXIES))
        if unknown:
            raise ValueError(f"Proxy không nằm trong thiết kế: {unknown}")
        proxies: list[ProxySweep] = []
        for proxy in KNOWN_PROXIES:
            raw = raw_proxies.get(proxy, {"enabled": False})
            if not isinstance(raw, Mapping):
                raise ValueError(f"proxies.{proxy} phải là mapping.")
            enabled = bool(raw.get("enabled", False))
            parameter = raw.get("parameter")
            values = tuple(float(value) for value in raw.get("values", []))
            sweep = ProxySweep(
                proxy=proxy,
                enabled=enabled,
                parameter=None if parameter is None else str(parameter),
                values=values,
                left_joint_indices=tuple(int(value) for value in raw.get("left_joint_indices", [])),
                right_joint_indices=tuple(int(value) for value in raw.get("right_joint_indices", [])),
                freezing_duration_steps=int(raw.get("freezing_duration_steps", 0)),
                reason=None if raw.get("reason") is None else str(raw["reason"]),
            )
            sweep.validate()
            proxies.append(sweep)
        if not any(item.enabled for item in proxies):
            raise ValueError("Campaign phải bật ít nhất một proxy.")
        return cls(
            campaign_name=name,
            random_seeds=seeds,
            steps=steps,
            duration_s=duration_s,
            output_directory=output_directory,
            proxies=tuple(proxies),
            scientific_scope=str(data.get("scientific_scope", SCIENTIFIC_SCOPE)),
        )

    @classmethod
    def from_yaml(cls, path: str | Path) -> "CampaignConfig":
        with Path(path).open("r", encoding="utf-8") as handle:
            document = yaml.safe_load(handle) or {}
        if not isinstance(document, Mapping):
            raise ValueError("Campaign YAML phải có root là mapping.")
        return cls.from_mapping(document)

    @property
    def enabled_proxies(self) -> tuple[ProxySweep, ...]:
        return tuple(item for item in self.proxies if item.enabled)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "campaign_name": self.campaign_name,
            "random_seeds": list(self.random_seeds),
            "steps": self.steps,
            "duration_s": self.duration_s,
            "output_directory": self.output_directory,
            "proxies": {
                item.proxy: {
                    "enabled": item.enabled,
                    "parameter": item.parameter,
                    "values": list(item.values),
                    "left_joint_indices": list(item.left_joint_indices),
                    "right_joint_indices": list(item.right_joint_indices),
                    "freezing_duration_steps": item.freezing_duration_steps,
                    "reason": item.reason,
                }
                for item in self.proxies
            },
            "scientific_scope": self.scientific_scope,
        }


def load_campaign_config(path: str | Path) -> CampaignConfig:
    """Đọc và validate campaign YAML."""

    return CampaignConfig.from_yaml(path)


def run_experimental_campaign(
    *,
    campaign_config: str | Path,
    baseline_config: str | Path,
    target_path: str | Path,
    output_dir: str | Path | None,
    repo_root: str | Path | None = None,
    runtime_gate: RuntimeGate | None = None,
    condition_runner: ConditionRunner | None = None,
) -> dict[str, Any]:
    """Chạy campaign tuần tự trên FlyGym thật sau khi qua hai gate."""

    root = Path(repo_root or Path.cwd()).expanduser().resolve()
    config = load_campaign_config(campaign_config)
    configured_output = Path(output_dir or config.output_directory).expanduser()
    output = (
        configured_output
        if configured_output.is_absolute()
        else root / configured_output
    ).resolve()
    baseline = load_healthy_baseline_config(baseline_config)
    gate = runtime_gate or build_runtime_gate(root, target_path)
    gate_status = _gate_status(gate)
    if gate_status != PASS:
        return _write_waiting_status(
            output,
            config=config,
            gate=gate,
            target_path=target_path,
            status=gate_status,
        )

    step_error = _validate_steps(config, baseline)
    if step_error is not None:
        return _write_failed_status(output, config, gate, target_path, step_error, FAILED_CONFIG)

    runner = condition_runner or _default_runner(root)
    output.mkdir(parents=True, exist_ok=True)
    baseline_records: list[dict[str, Any]] = []
    condition_records: list[dict[str, Any]] = []
    failed = 0

    for seed in config.random_seeds:
        baseline_id = f"healthy_baseline_seed_{seed}"
        run_config = _campaign_runtime_config(baseline, config, seed, baseline_id)
        record = _execute_record(
            runner,
            run_config,
            None,
            baseline_id,
            output / "baseline" / f"seed_{seed:04d}.json",
        )
        baseline_records.append(record)
        if record["status"] != "COMPLETED":
            failed += 1

        for sweep in config.enabled_proxies:
            for value in sweep.values:
                condition_id = f"{sweep.proxy}_{_value_token(value)}_seed_{seed}"
                run_config = _campaign_runtime_config(baseline, config, seed, condition_id)
                try:
                    layer = sweep.layer(value, seed, condition_id)
                except Exception as error:
                    record = _failed_record(condition_id, sweep.proxy, value, seed, error)
                else:
                    record = _execute_record(
                        runner,
                        run_config,
                        layer,
                        condition_id,
                        output / "conditions" / sweep.proxy / _value_token(value) / f"seed_{seed:04d}.json",
                        proxy=sweep.proxy,
                        parameter_value=value,
                    )
                condition_records.append(record)
                if record["status"] != "COMPLETED":
                    failed += 1

    campaign = {
        "campaign_name": config.campaign_name,
        "baseline": baseline_records,
        "conditions": condition_records,
        "config": config.to_mapping(),
        "scientific_scope": config.scientific_scope,
    }
    surface = build_response_surface(campaign)
    sensitivity = build_parameter_sensitivity(surface)
    status = PASS if failed == 0 else FAILED
    payload = {
        "schema_version": "1.0",
        "campaign_name": config.campaign_name,
        "status": status,
        "runtime_status": PASS,
        "target_status": PASS,
        "counts": {
            "completed": len(baseline_records) + sum(item["status"] == "COMPLETED" for item in condition_records),
            "failed": failed,
            "waiting": 0,
        },
        "parameter_count": len(config.enabled_proxies),
        "condition_count": len(condition_records),
        "gate": _gate_mapping(gate),
        "scientific_scope": config.scientific_scope,
        "artifacts": {},
    }
    _write_json(output / "campaign_data.json", campaign)
    paths = {
        "response_surface_csv": _write_csv(output / "response_surface.csv", surface["rows"]),
        "response_surface_json": _write_json(output / "response_surface.json", surface),
        "parameter_sensitivity_csv": _write_csv(output / "parameter_sensitivity.csv", sensitivity["rows"]),
        "parameter_sensitivity_json": _write_json(output / "parameter_sensitivity.json", sensitivity),
    }
    _write_campaign_markdown(output, payload, surface, sensitivity)
    paths.update({
        "experiment_summary": output / "experiment_summary.md",
        "campaign_status": output / "campaign_status.md",
    })
    payload["artifacts"] = {name: path.as_posix() for name, path in paths.items()}
    _write_json(output / "campaign_status.json", payload)
    return payload


def build_response_surface(campaign: Mapping[str, Any]) -> dict[str, Any]:
    """Gom metric theo proxy/value/metric từ các replicate đã chạy."""

    baseline = _aggregate_records(campaign.get("baseline", []), None, None)
    grouped: dict[tuple[str, float, str], list[float]] = {}
    for record in campaign.get("conditions", []):
        if record.get("status") != "COMPLETED":
            continue
        proxy = str(record.get("proxy", ""))
        value = float(record["parameter_value"])
        metrics = record.get("metrics", {})
        if not isinstance(metrics, Mapping):
            continue
        for metric_name, source_key in METRIC_SOURCES.items():
            if source_key is None:
                continue
            observed = _finite_or_none(metrics.get(source_key))
            if observed is not None:
                grouped.setdefault((proxy, value, metric_name), []).append(observed)

    rows: list[dict[str, Any]] = []
    for proxy, definition in campaign.get("config", {}).get("proxies", {}).items():
        if not definition.get("enabled"):
            continue
        for raw_value in definition.get("values", []):
            value = float(raw_value)
            for metric_name, source_key in METRIC_SOURCES.items():
                values = grouped.get((proxy, value, metric_name), [])
                rows.append({
                    "parameter": proxy,
                    "parameter_value": value,
                    "metric": metric_name,
                    "mean": _mean(values),
                    "std": _std(values),
                    "seed_count": len(values),
                    "healthy_mean": baseline.get(metric_name),
                    "status": "PASS" if values else "UNAVAILABLE_METRIC",
                    "source_metric": source_key or "",
                })
    return {
        "schema_version": "1.0",
        "scientific_scope": SCIENTIFIC_SCOPE,
        "rows": rows,
        "metric_sources": METRIC_SOURCES,
        "empty_values_mean_unavailable": True,
    }


def build_parameter_sensitivity(surface: Mapping[str, Any]) -> dict[str, Any]:
    """Xếp hạng độ nhạy computational từ các metric đã quan sát."""

    grouped: dict[str, list[float]] = {}
    metric_counts: dict[str, set[str]] = {}
    for row in surface.get("rows", []):
        if row.get("status") != "PASS":
            continue
        candidate = _finite_or_none(row.get("mean"))
        healthy = _finite_or_none(row.get("healthy_mean"))
        if candidate is None or healthy is None:
            continue
        scale = abs(healthy) if abs(healthy) > 1e-12 else 1.0
        grouped.setdefault(str(row["parameter"]), []).append(abs(candidate - healthy) / scale)
        metric_counts.setdefault(str(row["parameter"]), set()).add(str(row["metric"]))
    rows = []
    proxies = sorted({str(row.get("parameter")) for row in surface.get("rows", [])})
    for proxy in proxies:
        values = grouped.get(proxy, [])
        rows.append({
            "parameter": proxy,
            "mean_absolute_normalized_delta": _mean(values),
            "max_absolute_normalized_delta": max(values) if values else None,
            "metric_count": len(metric_counts.get(proxy, set())),
            "point_count": len(values),
            "status": "PASS" if values else "UNAVAILABLE_METRICS",
        })
    available = [row for row in rows if row["status"] == "PASS"]
    available.sort(key=lambda row: (-float(row["mean_absolute_normalized_delta"]), row["parameter"]))
    for rank, row in enumerate(available, start=1):
        row["rank"] = rank
    for row in rows:
        row.setdefault("rank", None)
    rows.sort(key=lambda row: (row["rank"] is None, row["rank"] or 0, row["parameter"]))
    return {
        "schema_version": "1.0",
        "scientific_scope": SCIENTIFIC_SCOPE,
        "rows": rows,
        "ranking_basis": "mean absolute normalized candidate-minus-Healthy delta across available metrics and values",
    }


def _gate_status(gate: RuntimeGate) -> str:
    if not gate.runtime_ready:
        return WAITING_RUNTIME
    if not gate.target_ready:
        return WAITING_TARGET_DATA
    return PASS


def _gate_mapping(gate: RuntimeGate) -> dict[str, Any]:
    """Return gate metadata with the campaign's truthful aggregate status."""

    mapping = gate.to_mapping()
    mapping["overall_status"] = _gate_status(gate)
    mapping["runtime_status"] = WAITING_RUNTIME if not gate.runtime_ready else PASS
    mapping["target_status"] = WAITING_TARGET_DATA if not gate.target_ready else PASS
    return mapping


def _validate_steps(config: CampaignConfig, baseline: HealthyBaselineConfig) -> str | None:
    expected = int(round(config.duration_s / baseline.timestep_s))
    if expected != config.steps:
        return (
            f"steps={config.steps} không khớp duration_s/timestep_s={expected}; "
            "không chạy simulation."
        )
    return None


def _default_runner(root: Path) -> ConditionRunner:
    def runner(config: HealthyBaselineConfig, layer: DiseaseLayer | None, condition_id: str) -> dict[str, Any]:
        return run_locomotion(
            config,
            repo_root=root,
            perturbation=layer,
            condition_id=condition_id,
            include_condition_metadata=True,
        )

    return runner


def _campaign_runtime_config(
    baseline: HealthyBaselineConfig,
    campaign: CampaignConfig,
    seed: int,
    experiment_id: str,
) -> HealthyBaselineConfig:
    data = deepcopy(baseline.data)
    data["experiment_id"] = experiment_id
    data["random_seed"] = seed
    data.setdefault("simulation", {})["duration_s"] = campaign.duration_s
    return HealthyBaselineConfig.from_mapping(data)


def _execute_record(
    runner: ConditionRunner,
    config: HealthyBaselineConfig,
    layer: DiseaseLayer | None,
    condition_id: str,
    path: Path,
    *,
    proxy: str = "healthy",
    parameter_value: float | None = None,
) -> dict[str, Any]:
    try:
        report = runner(config, layer, condition_id)
        status = "COMPLETED" if report.get("overall_pass") is True else "FAILED"
        record = {
            "condition_id": condition_id,
            "proxy": proxy,
            "parameter_value": parameter_value,
            "seed": config.random_seed,
            "status": status,
            "metrics": dict(report.get("derived_locomotion_metrics", {})),
            "report": report,
        }
    except Exception as error:  # noqa: BLE001 - preserve per-condition failure
        record = _failed_record(condition_id, proxy, parameter_value, config.random_seed, error)
    _write_json(path, record)
    return record


def _failed_record(condition_id: str, proxy: str, value: float | None, seed: int, error: BaseException) -> dict[str, Any]:
    return {
        "condition_id": condition_id,
        "proxy": proxy,
        "parameter_value": value,
        "seed": seed,
        "status": "FAILED",
        "metrics": {},
        "error_type": type(error).__name__,
        "error": str(error),
    }


def _aggregate_records(records: Sequence[Mapping[str, Any]], proxy: str | None, value: float | None) -> dict[str, float]:
    grouped: dict[str, list[float]] = {}
    for record in records:
        if record.get("status") != "COMPLETED":
            continue
        if proxy is not None and record.get("proxy") != proxy:
            continue
        if value is not None and not math.isclose(float(record.get("parameter_value")), value):
            continue
        metrics = record.get("metrics", {})
        if not isinstance(metrics, Mapping):
            continue
        for metric_name, source_key in METRIC_SOURCES.items():
            if source_key is not None:
                observed = _finite_or_none(metrics.get(source_key))
                if observed is not None:
                    grouped.setdefault(metric_name, []).append(observed)
    return {metric: float(sum(values) / len(values)) for metric, values in grouped.items() if values}


def _write_waiting_status(
    output: Path,
    *,
    config: CampaignConfig,
    gate: RuntimeGate,
    target_path: str | Path,
    status: str,
) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    reason = (
        "Runtime FlyGym chưa sẵn sàng; không chạy simulation."
        if status == WAITING_RUNTIME
        else "Chưa có approved numeric calibration targets; không chạy simulation."
    )
    payload = {
        "schema_version": "1.0",
        "campaign_name": config.campaign_name,
        "status": status,
        "runtime_status": WAITING_RUNTIME if not gate.runtime_ready else PASS,
        "target_status": WAITING_TARGET_DATA if not gate.target_ready else PASS,
        "counts": {"completed": 0, "failed": 0, "waiting": 0},
        "scientific_results_generated": False,
        "target_path": str(Path(target_path).expanduser().resolve()),
        "gate": _gate_mapping(gate),
        "reason": reason,
        "next_action": "Sửa runtime hoặc cung cấp approved numeric targets rồi chạy lại campaign.",
        "scientific_scope": config.scientific_scope,
    }
    _write_json(output / "campaign_status.json", payload)
    (output / "campaign_status.md").write_text(
        "# Trạng thái Experimental Campaign v1\n\n"
        f"- Trạng thái: `{status}`\n"
        f"- Campaign: `{config.campaign_name}`\n"
        f"- Lý do: {reason}\n\n"
        "Không tạo dataset, response surface, sensitivity ranking hoặc figure.\n\n"
        f"Phạm vi: {config.scientific_scope}\n",
        encoding="utf-8",
    )
    return payload


def _write_failed_status(
    output: Path,
    config: CampaignConfig,
    gate: RuntimeGate,
    target_path: str | Path,
    error: str,
    status: str,
) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "campaign_name": config.campaign_name,
        "status": status,
        "counts": {"completed": 0, "failed": 0, "waiting": 0},
        "scientific_results_generated": False,
        "target_path": str(Path(target_path).expanduser().resolve()),
        "gate": _gate_mapping(gate),
        "error": error,
        "scientific_scope": config.scientific_scope,
    }
    _write_json(output / "campaign_status.json", payload)
    (output / "campaign_status.md").write_text(
        "# Trạng thái Experimental Campaign v1\n\n"
        f"- Trạng thái: `{status}`\n"
        f"- Lỗi cấu hình: {error}\n\n"
        "Không chạy simulation và không tạo response surface.\n",
        encoding="utf-8",
    )
    return payload


def _write_campaign_markdown(
    output: Path,
    payload: Mapping[str, Any],
    surface: Mapping[str, Any],
    sensitivity: Mapping[str, Any],
) -> None:
    summary = [
        "# Tóm tắt Experimental Campaign v1",
        "",
        f"- Trạng thái: `{payload['status']}`",
        f"- Runtime: `{payload['runtime_status']}`",
        f"- Target: `{payload['target_status']}`",
        f"- Số proxy bật: `{payload['parameter_count']}`",
        f"- Số condition: `{payload['condition_count']}`",
        f"- Completed: `{payload['counts']['completed']}`",
        f"- Failed: `{payload['counts']['failed']}`",
        "- Waiting: `0`",
        "",
        "Đây là computational locomotion experiment; không phải biological validation, clinical prediction hoặc drug response.",
    ]
    (output / "experiment_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")

    surface_lines = [
        "# Response Surface",
        "",
        "Các giá trị mean/std chỉ được tính từ replicate đã chạy thành công.",
        "",
        "| Parameter | Value | Metric | Mean | Std | Seed count | Status |",
        "| --- | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for row in surface.get("rows", []):
        surface_lines.append(_table_row(row, ("parameter", "parameter_value", "metric", "mean", "std", "seed_count", "status")))
    (output / "response_surface.md").write_text("\n".join(surface_lines) + "\n", encoding="utf-8")

    sensitivity_lines = [
        "# Xếp hạng độ nhạy parameter",
        "",
        "Xếp hạng này là độ nhạy computational, dựa trên normalized delta so với Healthy; không phải mức độ bệnh.",
        "",
        "| Rank | Parameter | Mean abs normalized delta | Max abs normalized delta | Metric count | Point count | Status |",
        "| ---: | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in sensitivity.get("rows", []):
        sensitivity_lines.append(_table_row(row, ("rank", "parameter", "mean_absolute_normalized_delta", "max_absolute_normalized_delta", "metric_count", "point_count", "status")))
    (output / "parameter_sensitivity.md").write_text("\n".join(sensitivity_lines) + "\n", encoding="utf-8")

    status_lines = [
        "# Trạng thái Experimental Campaign v1",
        "",
        f"- Trạng thái: `{payload['status']}`",
        f"- Completed: `{payload['counts']['completed']}`",
        f"- Failed: `{payload['counts']['failed']}`",
        "- Waiting: `0`",
        "",
        f"Phạm vi: {payload['scientific_scope']}",
    ]
    (output / "campaign_status.md").write_text("\n".join(status_lines) + "\n", encoding="utf-8")


def _table_row(row: Mapping[str, Any], fields: Sequence[str]) -> str:
    return "| " + " | ".join(_display(row.get(field)) for field in fields) + " |"


def _display(value: Any) -> str:
    if value is None or value == "":
        return "-"
    if isinstance(value, float):
        return f"{value:.8g}"
    return str(value).replace("|", "\\|")


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> Path:
    fields = list(rows[0].keys()) if rows else ["parameter", "parameter_value", "metric", "mean", "std", "seed_count", "status"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path


def _write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return path


def _value_token(value: float) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", f"{value:g}").strip("_") or "zero"


def _finite_or_none(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _mean(values: Sequence[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _std(values: Sequence[float]) -> float | None:
    if not values:
        return None
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))


__all__ = [
    "CampaignConfig",
    "FAILED",
    "FAILED_CONFIG",
    "KNOWN_PROXIES",
    "METRIC_SOURCES",
    "PASS",
    "ProxySweep",
    "SCIENTIFIC_SCOPE",
    "WAITING_RUNTIME",
    "WAITING_TARGET_DATA",
    "build_parameter_sensitivity",
    "build_response_surface",
    "load_campaign_config",
    "run_experimental_campaign",
]
