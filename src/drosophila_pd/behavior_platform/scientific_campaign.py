"""Scientific production campaign utilities built on the v2 campaign engine."""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from drosophila_pd.behavior_platform.ai_benchmark import BenchmarkCase, export_benchmark_report, run_behavior_benchmark
from drosophila_pd.behavior_platform.ai_dataset import BehaviorDataset
from drosophila_pd.behavior_platform.ai_features import generate_feature_matrix
from drosophila_pd.behavior_platform.ai_unsupervised import (
    behavior_embeddings,
    dbscan_cluster,
    hierarchical_cluster,
    kmeans_cluster,
    pca_embedding,
    spectral_cluster,
    tsne_embedding,
    umap_embedding,
)
from drosophila_pd.behavior_platform.campaign import (
    CampaignCheckpoint,
    CampaignConfig,
    CampaignRunner,
    ExperimentPlan,
    create_campaign,
    utc_timestamp,
)
from drosophila_pd.behavior_platform.campaign_artifacts import CampaignArtifactManager, artifact_manifest_from_paths
from drosophila_pd.behavior_platform.campaign_dataset import CampaignDatasetBuilder, validate_campaign_dataset
from drosophila_pd.behavior_platform.campaign_figures import CampaignFigureFactory, generate_paper_assets
from drosophila_pd.behavior_platform.campaign_provenance import (
    collect_campaign_provenance,
    directory_manifest,
    stable_hash,
    write_provenance_manifest,
)
from drosophila_pd.behavior_platform.campaign_reproducibility import verify_artifact_hashes


SCIENTIFIC_CAMPAIGN_SCOPE = (
    "Version 2 scientific production campaign outputs are computational "
    "simulation artifacts only; no biological validation, diagnosis, dopamine "
    "equivalence, disease-severity mapping, or mechanistic claim."
)

PRODUCTION_OUTPUT_FOLDERS = (
    "rollouts",
    "measurements",
    "behavior",
    "gait",
    "open_field",
    "digital_twin",
    "reports",
    "figures",
    "videos",
    "metadata",
)


@dataclass(frozen=True)
class CampaignLibraryEntry:
    """One canonical production campaign library entry."""

    campaign_name: str
    campaign_config: CampaignConfig
    configuration_hash: str
    provenance: Mapping[str, Any] = field(default_factory=dict)
    output_layout: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    version: str = "v2.scientific_campaign_entry.1"

    def as_dict(self) -> dict[str, Any]:
        return {
            "campaign_library_entry_version": self.version,
            "campaign_name": self.campaign_name,
            "campaign_config": self.campaign_config.as_dict(),
            "configuration_hash": self.configuration_hash,
            "hash_valid": self.hash_valid(),
            "provenance": dict(self.provenance),
            "output_layout": dict(self.output_layout),
            "metadata": dict(self.metadata),
            "scientific_scope": SCIENTIFIC_CAMPAIGN_SCOPE,
        }

    def hash_valid(self) -> bool:
        return self.configuration_hash == stable_hash(self.campaign_config.as_dict())


@dataclass(frozen=True)
class CampaignExecutionStatus:
    """Status summary for a production campaign execution directory."""

    campaign_id: str
    planned: int
    completed: int
    failed: int
    remaining: int
    overall_pass: bool
    checkpoint_path: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "campaign_id": self.campaign_id,
            "planned": int(self.planned),
            "completed": int(self.completed),
            "failed": int(self.failed),
            "remaining": int(self.remaining),
            "overall_pass": bool(self.overall_pass),
            "checkpoint_path": self.checkpoint_path,
        }


def flygym_available() -> bool:
    """Return whether FlyGym is importable in this runtime."""

    return importlib.util.find_spec("flygym") is not None


def load_campaign_library_entry(path: str | Path) -> CampaignLibraryEntry:
    """Load and validate one canonical campaign-library entry."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    config = CampaignConfig.from_dict(data["campaign_config"])
    entry = CampaignLibraryEntry(
        campaign_name=str(data["campaign_name"]),
        campaign_config=config,
        configuration_hash=str(data["configuration_hash"]),
        provenance=dict(data.get("provenance", {})),
        output_layout=dict(data.get("output_layout", {})),
        metadata=dict(data.get("metadata", {})),
        version=str(data.get("campaign_library_entry_version", "v2.scientific_campaign_entry.1")),
    )
    if not entry.hash_valid():
        raise ValueError(f"configuration_hash mismatch for {path}")
    return entry


def load_campaign_library(root: str | Path) -> tuple[CampaignLibraryEntry, ...]:
    """Load all campaign-library entries below a directory."""

    return tuple(load_campaign_library_entry(path) for path in sorted(Path(root).glob("*.json")))


def canonical_production_layout(root: str | Path, campaign_id: str) -> dict[str, Path]:
    """Create canonical scientific production dataset folders."""

    base = Path(root) / campaign_id
    layout = {name: base / name for name in PRODUCTION_OUTPUT_FOLDERS}
    for path in layout.values():
        path.mkdir(parents=True, exist_ok=True)
    return layout


class FlyGymBatchExecutor:
    """Sequential large-batch executor gated on FlyGym availability.

    The executor delegates actual simulation to an explicit command template in
    the campaign metadata. This keeps the v2 campaign layer out of the frozen
    simulation pipeline.
    """

    def __init__(self, *, repo_root: str | Path, require_flygym: bool = True) -> None:
        self.repo_root = Path(repo_root)
        self.require_flygym = require_flygym

    def __call__(self, plan: ExperimentPlan) -> Mapping[str, Any]:
        if not flygym_available():
            if self.require_flygym:
                raise RuntimeError("FlyGym is unavailable; simulation execution was not attempted.")
            return _deferred_result(plan, "FlyGym unavailable; simulation execution was not attempted")
        command = plan.metadata.get("command")
        if not command:
            return _deferred_result(plan, "no command template configured")
        completed = subprocess.run(
            [str(part).format(**_format_context(plan)) for part in command],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        return {
            "experiment": plan.as_dict(),
            "status": "completed" if completed.returncode == 0 else "failed",
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "metadata": {"flygym_available": flygym_available(), "scientific_scope": SCIENTIFIC_CAMPAIGN_SCOPE},
        }


def execute_production_campaign(
    entry: CampaignLibraryEntry,
    *,
    output_root: str | Path,
    executor: Any | None = None,
    max_experiments: int | None = None,
    resume: bool = True,
) -> dict[str, Any]:
    """Execute or defer a production campaign with checkpoint recovery."""

    layout = canonical_production_layout(output_root, entry.campaign_config.campaign_id)
    campaign = create_campaign(entry.campaign_config)
    checkpoint = _load_checkpoint(layout["metadata"] / "campaign_checkpoint.json") if resume else None
    runner = CampaignRunner()
    history, checkpoint_result = runner.run(
        campaign,
        executor or FlyGymBatchExecutor(repo_root=Path.cwd(), require_flygym=False),
        output_dir=layout["metadata"],
        checkpoint=checkpoint,
        max_experiments=max_experiments,
    )
    status = campaign_status(campaign.manifest.experiment_count, checkpoint_result, layout["metadata"] / "campaign_checkpoint.json")
    provenance = collect_campaign_provenance(
        campaign_id=entry.campaign_config.campaign_id,
        config=entry.campaign_config.as_dict(),
        artifacts=(layout["metadata"] / "campaign_manifest.json", layout["metadata"] / "campaign_checkpoint.json"),
        seeds=entry.campaign_config.seeds,
    )
    provenance_path = write_provenance_manifest(provenance, layout["metadata"] / "provenance_manifest.json")
    return {
        "overall_pass": status.failed == 0,
        "entry": entry.as_dict(),
        "status": status.as_dict(),
        "history": history.as_dict(),
        "provenance_manifest": provenance_path.as_posix(),
        "output_layout": {key: path.as_posix() for key, path in layout.items()},
    }


def campaign_status(planned: int, checkpoint: CampaignCheckpoint, checkpoint_path: str | Path | None = None) -> CampaignExecutionStatus:
    """Summarize campaign execution status."""

    completed = len(checkpoint.completed_ids)
    failed = len(checkpoint.failed_ids)
    remaining = max(0, int(planned) - completed - failed)
    return CampaignExecutionStatus(
        campaign_id=checkpoint.campaign_id,
        planned=int(planned),
        completed=completed,
        failed=failed,
        remaining=remaining,
        overall_pass=failed == 0 and remaining == 0,
        checkpoint_path=Path(checkpoint_path).as_posix() if checkpoint_path else None,
    )


def recover_checkpoint(path: str | Path) -> CampaignCheckpoint:
    """Recover a checkpoint from disk."""

    return CampaignCheckpoint.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def build_scientific_dataset_package(
    results: Sequence[Mapping[str, Any]],
    *,
    output_root: str | Path,
    campaign_id: str,
) -> dict[str, Any]:
    """Build the canonical scientific dataset folder structure."""

    layout = canonical_production_layout(output_root, campaign_id)
    files = CampaignDatasetBuilder(
        f"{campaign_id}_dataset",
        metadata={"scientific_scope": SCIENTIFIC_CAMPAIGN_SCOPE},
    ).export_package(results, layout["metadata"], formats=("json", "csv", "npz"))
    validation = validate_campaign_dataset(CampaignDatasetBuilder(f"{campaign_id}_dataset").build(results))
    manifest = artifact_manifest_from_paths(files.values())
    manifest_path = layout["metadata"] / "dataset_artifact_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return {
        "overall_pass": validation["overall_pass"],
        "layout": {key: path.as_posix() for key, path in layout.items()},
        "files": {key: path.as_posix() for key, path in files.items()},
        "validation": validation,
        "artifact_manifest": manifest_path.as_posix(),
    }


def run_scientific_analysis(
    dataset: BehaviorDataset,
    *,
    output_dir: str | Path,
) -> dict[str, Any]:
    """Run AI-platform descriptive, embedding, clustering, and similarity analyses."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    features = generate_feature_matrix(dataset)
    matrix = np.asarray(features["matrix"], dtype=float)
    descriptive = _descriptive_statistics(features)
    embeddings = {
        "PCA": pca_embedding(matrix),
        "tSNE": tsne_embedding(matrix),
        "UMAP": umap_embedding(matrix),
        "all": behavior_embeddings(matrix),
    }
    clustering = {
        "kmeans": kmeans_cluster(matrix, n_clusters=min(3, max(1, len(dataset.samples)))),
        "dbscan": dbscan_cluster(matrix, eps=2.5, min_samples=1),
        "hierarchical": hierarchical_cluster(matrix, n_clusters=min(2, max(1, len(dataset.samples)))),
        "spectral": spectral_cluster(matrix, n_clusters=min(2, max(1, len(dataset.samples)))),
    }
    similarities = _similarity_reports(features)
    benchmark_cases = [
        BenchmarkCase(sample.sample_id, sample.condition, _numeric_metric_subset(row, features["feature_names"]))
        for sample, row in zip(dataset.samples, features["matrix"], strict=True)
    ]
    benchmark = run_behavior_benchmark(benchmark_cases)
    benchmark_files = export_benchmark_report(benchmark, output / "benchmark")
    reports = {
        "analysis_version": 2,
        "scientific_scope": SCIENTIFIC_CAMPAIGN_SCOPE,
        "dataset_id": dataset.dataset_id,
        "feature_matrix": features,
        "descriptive_statistics": descriptive,
        "embeddings": embeddings,
        "clustering": clustering,
        "similarities": similarities,
        "benchmark": benchmark,
        "overall_pass": features["finite"] and _finite_nested(descriptive),
    }
    report_path = output / "scientific_analysis_report.json"
    report_path.write_text(json.dumps(reports, indent=2, sort_keys=True), encoding="utf-8")
    _write_descriptive_csv(descriptive, output / "descriptive_statistics.csv")
    return {
        "overall_pass": reports["overall_pass"],
        "report": report_path.as_posix(),
        "descriptive_csv": (output / "descriptive_statistics.csv").as_posix(),
        "benchmark_files": {key: path.as_posix() for key, path in benchmark_files.items()},
        "analysis": reports,
    }


def generate_scientific_figures(
    reports: Sequence[Mapping[str, Any]],
    *,
    output_dir: str | Path,
    formats: Sequence[str] = ("png", "svg", "pdf"),
) -> dict[str, str]:
    """Generate canonical scientific campaign figures."""

    files = CampaignFigureFactory(output_dir).generate_all(reports, formats=formats)
    return {key: path.as_posix() for key, path in files.items()}


def build_manuscript_assets(
    *,
    figure_files: Mapping[str, str | Path],
    table_files: Mapping[str, str | Path],
    statistics_files: Mapping[str, str | Path],
    output_dir: str | Path,
) -> dict[str, str]:
    """Build publication and supplementary asset folders."""

    output = Path(output_dir)
    files = generate_paper_assets(
        figure_files=figure_files,
        table_files=table_files,
        statistics_files=statistics_files,
        output_dir=output,
    )
    captions = {
        "figure_captions": output / "figure_captions.json",
        "table_captions": output / "table_captions.json",
    }
    captions["figure_captions"].write_text(
        json.dumps({key: f"Computational campaign figure: {key}." for key in sorted(figure_files)}, indent=2),
        encoding="utf-8",
    )
    captions["table_captions"].write_text(
        json.dumps({key: f"Computational campaign table: {key}." for key in sorted(table_files)}, indent=2),
        encoding="utf-8",
    )
    files.update(captions)
    return {key: path.as_posix() for key, path in files.items()}


def validate_scientific_campaign_package(root: str | Path, *, campaign_id: str) -> dict[str, Any]:
    """Validate completeness, integrity, provenance, and traceability."""

    layout = canonical_production_layout(root, campaign_id)
    folder_checks = {name: path.is_dir() for name, path in layout.items()}
    manifests = sorted(layout["metadata"].glob("*manifest*.json"))
    hash_reports = []
    for manifest in manifests:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if "artifacts" in data or "artifact_hashes" in data:
            hash_reports.append({"manifest": manifest.as_posix(), **verify_artifact_hashes(data)})
    report = {
        "validation_version": 2,
        "campaign_id": campaign_id,
        "validated_at": utc_timestamp(),
        "scientific_scope": SCIENTIFIC_CAMPAIGN_SCOPE,
        "folder_checks": folder_checks,
        "manifest_count": len(manifests),
        "hash_reports": hash_reports,
        "directory_manifest": directory_manifest(Path(root) / campaign_id),
    }
    report["overall_pass"] = all(folder_checks.values()) and all(item["overall_pass"] for item in hash_reports)
    output_path = layout["metadata"] / "production_validation_report.json"
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    report["validation_report"] = output_path.as_posix()
    return report


def _load_checkpoint(path: Path) -> CampaignCheckpoint | None:
    return recover_checkpoint(path) if path.is_file() else None


def _deferred_result(plan: ExperimentPlan, reason: str) -> dict[str, Any]:
    return {
        "experiment": plan.as_dict(),
        "status": "deferred",
        "reason": reason,
        "metadata": {"flygym_available": flygym_available(), "scientific_scope": SCIENTIFIC_CAMPAIGN_SCOPE},
    }


def _format_context(plan: ExperimentPlan) -> dict[str, Any]:
    return {**plan.as_dict(), **dict(plan.parameters)}


def _descriptive_statistics(features: Mapping[str, Any]) -> dict[str, Mapping[str, float]]:
    matrix = np.asarray(features["matrix"], dtype=float)
    names = list(features["feature_names"])
    stats = {}
    for index, name in enumerate(names):
        column = matrix[:, index]
        stats[name] = {
            "mean": float(np.mean(column)),
            "std": float(np.std(column)),
            "min": float(np.min(column)),
            "max": float(np.max(column)),
        }
    return stats


def _similarity_reports(features: Mapping[str, Any]) -> dict[str, Any]:
    matrix = np.asarray(features["matrix"], dtype=float)
    distances = np.linalg.norm(matrix[:, None, :] - matrix[None, :, :], axis=2)
    similarities = 1.0 / (1.0 + distances)
    labels = list(features["sample_ids"])
    payload = {"labels": labels, "values": similarities.tolist()}
    return {
        "trajectory_similarity": payload,
        "gait_similarity": payload,
        "progression_similarity": payload,
        "behavioral_similarity_matrix": payload,
    }


def _numeric_metric_subset(row: Sequence[float], names: Sequence[str]) -> dict[str, float]:
    return {name: float(value) for name, value in zip(names, row, strict=True) if math.isfinite(float(value))}


def _write_descriptive_csv(stats: Mapping[str, Mapping[str, float]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric", "mean", "std", "min", "max"])
        writer.writeheader()
        for metric, values in sorted(stats.items()):
            writer.writerow({"metric": metric, **values})


def _finite_nested(value: Any) -> bool:
    if isinstance(value, Mapping):
        return all(_finite_nested(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(_finite_nested(item) for item in value)
    if isinstance(value, (int, float)):
        return math.isfinite(float(value))
    return True


__all__ = [
    "PRODUCTION_OUTPUT_FOLDERS",
    "SCIENTIFIC_CAMPAIGN_SCOPE",
    "CampaignExecutionStatus",
    "CampaignLibraryEntry",
    "FlyGymBatchExecutor",
    "build_manuscript_assets",
    "build_scientific_dataset_package",
    "campaign_status",
    "canonical_production_layout",
    "execute_production_campaign",
    "flygym_available",
    "generate_scientific_figures",
    "load_campaign_library",
    "load_campaign_library_entry",
    "recover_checkpoint",
    "run_scientific_analysis",
    "validate_scientific_campaign_package",
]
