"""Experiment suite manager built on the existing rollout analysis API."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import shutil
import time
from typing import Any, Mapping, Sequence

from drosophila_pd.analysis import AnalysisResult, LoadedRollout, analyze_rollout, load_rollout

from .config import ExperimentConfig, load_experiment_configs
from .report import write_comparison_report, write_final_report


EXPERIMENT_STATUSES = ("COMPLETED", "WAITING_DATASET", "FAILED", "SKIPPED")
SUITE_SCOPE = (
    "Sequential computational experiment orchestration over imported rollout data only; "
    "no FlyGym execution, fabricated data, biological validation, or clinical claim."
)
SCALAR_METRICS = (
    "walking_speed_mm_s",
    "total_distance_mm",
    "com_velocity_mean_mm_s",
    "heading_variance_rad2",
    "stride_frequency_hz",
    "step_frequency_hz",
    "body_orientation_variance_rad2",
    "symmetry_index",
    "trajectory_curvature_mean_rad_per_mm",
)


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Path):
        return value.as_posix()
    return value


def _write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return path


@dataclass
class ExperimentRecord:
    """Persisted status and artifact inventory for one experiment."""

    experiment_id: str
    name: str
    condition: str
    dataset: Path
    output_root: Path
    status: str = "WAITING_DATASET"
    seed: int | None = None
    config_hash: str = ""
    started_at: str | None = None
    finished_at: str | None = None
    duration_s: float | None = None
    metrics: Mapping[str, Any] = field(default_factory=dict)
    artifacts: Mapping[str, str] = field(default_factory=dict)
    error: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "condition": self.condition,
            "dataset": self.dataset.as_posix(),
            "output_root": self.output_root.as_posix(),
            "status": self.status,
            "seed": self.seed,
            "config_hash": self.config_hash,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_s": self.duration_s,
            "metrics": _jsonable(self.metrics),
            "artifacts": dict(self.artifacts),
            "error": self.error,
        }

    @classmethod
    def from_file(cls, path: str | Path) -> "ExperimentRecord":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"Experiment record must be an object: {path}")
        return cls(
            experiment_id=str(payload["experiment_id"]),
            name=str(payload.get("name", payload["experiment_id"])),
            condition=str(payload.get("condition", "")),
            dataset=Path(str(payload.get("dataset", ""))),
            output_root=Path(str(payload.get("output_root", Path(path).parent))),
            status=str(payload.get("status", "FAILED")),
            seed=payload.get("seed"),
            config_hash=str(payload.get("config_hash", "")),
            started_at=payload.get("started_at"),
            finished_at=payload.get("finished_at"),
            duration_s=payload.get("duration_s"),
            metrics=dict(payload.get("metrics", {})),
            artifacts=dict(payload.get("artifacts", {})),
            error=str(payload.get("error", "")),
        )


class ExperimentManager:
    """Run configured experiments sequentially and build suite comparisons."""

    def __init__(
        self,
        repository_root: str | Path = ".",
        *,
        output_root: str | Path = "results/experiments",
        config_dir: str | Path = "experiments",
    ) -> None:
        self.repository_root = Path(repository_root).expanduser().resolve()
        self.output_root = (self.repository_root / output_root).resolve() if not Path(output_root).is_absolute() else Path(output_root).resolve()
        self.config_dir = (self.repository_root / config_dir).resolve() if not Path(config_dir).is_absolute() else Path(config_dir).resolve()
        self.output_root.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        configs: Sequence[str | Path] | None = None,
        *,
        resume: bool = True,
    ) -> dict[str, Any]:
        """Run every configured experiment in order and write suite artifacts."""

        loaded = load_experiment_configs(configs, config_dir=self.config_dir)
        records: list[ExperimentRecord] = []
        rollouts: dict[str, LoadedRollout] = {}
        for config in loaded:
            record, rollout = self._run_one(config, resume=resume)
            records.append(record)
            if rollout is not None:
                rollouts[record.experiment_id] = rollout

        comparison = write_comparison_report(records, rollouts, self.output_root / "comparison")
        summary = self._write_summary(loaded, records, comparison)
        final_report = write_final_report(summary, comparison, self.output_root / "final_report.html")
        summary["files"]["final_report"] = final_report.as_posix()
        _write_json(self.output_root / "experiment_summary.json", summary)
        return summary

    run_suite = run

    def _run_one(self, config: ExperimentConfig, *, resume: bool) -> tuple[ExperimentRecord, LoadedRollout | None]:
        experiment_root = self.output_root / config.experiment_id
        record_path = experiment_root / "experiment.json"
        dataset = config.dataset_path(self.repository_root)
        if resume and record_path.is_file():
            try:
                existing = ExperimentRecord.from_file(record_path)
                if existing.status == "COMPLETED" and (experiment_root / "metrics" / "metrics.json").is_file():
                    try:
                        loaded = load_rollout(dataset) if dataset.is_dir() else None
                    except (FileNotFoundError, OSError, ValueError):
                        loaded = None
                    if loaded is not None:
                        return existing, loaded
            except (OSError, ValueError, KeyError):
                pass

        record = ExperimentRecord(
            experiment_id=config.experiment_id,
            name=config.name,
            condition=config.condition,
            dataset=dataset,
            output_root=experiment_root,
            seed=config.seed,
            config_hash=config.config_hash(),
            started_at=_timestamp(),
        )
        started = time.perf_counter()
        rollout: LoadedRollout | None = None
        try:
            if not dataset.is_dir():
                record.status = "WAITING_DATASET"
                record.error = f"Dataset directory is not available: {dataset}"
                self._write_waiting_report(record, config)
            else:
                rollout = load_rollout(dataset)
                self._copy_rollout_artifacts(rollout, experiment_root / "rollout")
                result = analyze_rollout(dataset, experiment_root)
                record.status = "COMPLETED"
                record.metrics = result.metrics.get("scalar_metrics", {})
                record.artifacts = self._artifact_inventory(experiment_root)
        except FileNotFoundError as error:
            record.status = "WAITING_DATASET"
            record.error = str(error)
            self._write_waiting_report(record, config)
        except Exception as error:  # per-experiment isolation keeps the suite running
            record.status = "FAILED"
            record.error = f"{type(error).__name__}: {error}"
        record.finished_at = _timestamp()
        record.duration_s = time.perf_counter() - started
        _write_json(record_path, record.as_dict())
        return record, rollout

    def _copy_rollout_artifacts(self, rollout: LoadedRollout, target: Path) -> None:
        target.mkdir(parents=True, exist_ok=True)
        for source in rollout.source_files:
            shutil.copy2(source, target / source.name)
        metadata = rollout.dataset_dir / "metadata.json"
        if metadata.is_file() and metadata not in rollout.source_files:
            shutil.copy2(metadata, target / metadata.name)
        _write_json(target / "source_manifest.json", {
            "source_dataset": rollout.dataset_dir.as_posix(),
            "source_files": [source.name for source in rollout.source_files],
            "frame_count": rollout.frame_count,
            "scientific_scope": SUITE_SCOPE,
        })

    def _write_waiting_report(self, record: ExperimentRecord, config: ExperimentConfig) -> None:
        report = record.output_root / "report"
        report.mkdir(parents=True, exist_ok=True)
        (report / "summary.md").write_text(
            "# Experiment Summary\n\n"
            f"- Experiment: `{config.experiment_id}`\n"
            "- Status: `WAITING_DATASET`\n"
            f"- Dataset: `{record.dataset.as_posix()}`\n\n"
            "No rollout was found. No metrics, figures, or scientific result were generated.\n\n"
            f"Scope: {SUITE_SCOPE}\n",
            encoding="utf-8",
        )

    def _artifact_inventory(self, root: Path) -> dict[str, str]:
        paths: dict[str, str] = {}
        for category in ("rollout", "metrics", "report", "figures"):
            directory = root / category
            if directory.is_dir():
                for path in sorted(directory.rglob("*")):
                    if path.is_file():
                        paths[f"{category}/{path.relative_to(directory).as_posix()}"] = path.as_posix()
        return paths

    def _write_summary(
        self,
        configs: Sequence[ExperimentConfig],
        records: Sequence[ExperimentRecord],
        comparison: Mapping[str, Any],
    ) -> dict[str, Any]:
        rows = [record.as_dict() for record in records]
        counts = {status: sum(record.status == status for record in records) for status in EXPERIMENT_STATUSES}
        summary: dict[str, Any] = {
            "suite_version": 1,
            "generated_at": _timestamp(),
            "experiment_count": len(records),
            "counts": counts,
            "experiments": rows,
            "comparison": _jsonable(comparison),
            "files": {"comparison": (self.output_root / "comparison").as_posix()},
            "scientific_scope": SUITE_SCOPE,
            "config_files": [config.config_path.as_posix() for config in configs],
        }
        json_path = _write_json(self.output_root / "experiment_summary.json", summary)
        csv_path = self.output_root / "experiment_summary.csv"
        fields = ("experiment_id", "condition", "dataset", "status", *SCALAR_METRICS, "duration_s", "error")
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for record in records:
                row = record.as_dict()
                row.update(record.metrics)
                writer.writerow({field: row.get(field, "") for field in fields})
        summary["files"].update({"summary_json": json_path.as_posix(), "summary_csv": csv_path.as_posix()})
        return summary


def run_experiment_suite(
    configs: Sequence[str | Path] | None = None,
    *,
    repository_root: str | Path = ".",
    output_root: str | Path = "results/experiments",
    config_dir: str | Path = "experiments",
    resume: bool = True,
) -> dict[str, Any]:
    """Convenience entry point for the sequential experiment manager."""

    return ExperimentManager(repository_root, output_root=output_root, config_dir=config_dir).run(configs, resume=resume)


__all__ = ["EXPERIMENT_STATUSES", "ExperimentManager", "ExperimentRecord", "SCALAR_METRICS", "SUITE_SCOPE", "run_experiment_suite"]
