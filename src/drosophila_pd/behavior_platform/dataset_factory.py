"""Production dataset factory for completed v2 simulation campaigns."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from drosophila_pd.behavior_platform.ai_dataset import (
    BehaviorDataset,
    BehaviorSample,
    DatasetExporter,
    DatasetLoader,
    create_dataset_manifest,
    verify_dataset_integrity,
)
from drosophila_pd.behavior_platform.ai_examples import synthetic_behavior_dataset
from drosophila_pd.behavior_platform.ai_features import generate_feature_matrix
from drosophila_pd.behavior_platform.campaign import utc_timestamp
from drosophila_pd.behavior_platform.campaign_dataset import (
    CampaignDatasetBuilder,
    merge_campaign_datasets,
    validate_campaign_dataset,
)
from drosophila_pd.behavior_platform.campaign_provenance import file_sha256, stable_hash


DATASET_FACTORY_SCOPE = (
    "Version 2 dataset factory output is computational simulation data or "
    "clearly labeled synthetic demonstration data only; no biological "
    "validation, diagnosis, disease-severity mapping, dopamine equivalence, "
    "or mechanistic claim."
)

DATASET_EXPORT_FORMATS = ("json", "csv", "npz", "parquet", "arrow", "hdf5")


@dataclass(frozen=True)
class RolloutIndexEntry:
    """Index entry for one discovered completed rollout or report."""

    path: str
    sha256: str
    campaign_id: str
    sample_id: str
    condition: str
    has_arrays: bool
    has_metrics: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "sha256": self.sha256,
            "campaign_id": self.campaign_id,
            "sample_id": self.sample_id,
            "condition": self.condition,
            "has_arrays": bool(self.has_arrays),
            "has_metrics": bool(self.has_metrics),
        }


@dataclass(frozen=True)
class DatasetFactoryConfig:
    """Configuration for building a production dataset from campaign outputs."""

    dataset_id: str
    dataset_version: str = "v2.dataset.1"
    source_roots: tuple[str, ...] = ()
    output_dir: str = "outputs/v2/datasets"
    export_formats: tuple[str, ...] = ("json", "csv", "npz")
    split_ratios: Mapping[str, float] = field(
        default_factory=lambda: {"train": 0.7, "validation": 0.15, "test": 0.15}
    )
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "dataset_version": self.dataset_version,
            "source_roots": list(self.source_roots),
            "output_dir": self.output_dir,
            "export_formats": list(self.export_formats),
            "split_ratios": dict(self.split_ratios),
            "metadata": dict(self.metadata),
            "scientific_scope": DATASET_FACTORY_SCOPE,
        }


@dataclass(frozen=True)
class DatasetFactoryResult:
    """Summary returned by a dataset factory build."""

    dataset_id: str
    dataset_version: str
    sample_count: int
    cache_hit: bool
    files: Mapping[str, str]
    manifest_path: str
    validation: Mapping[str, Any]
    reports: Mapping[str, str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "dataset_version": self.dataset_version,
            "sample_count": int(self.sample_count),
            "cache_hit": bool(self.cache_hit),
            "files": dict(self.files),
            "manifest_path": self.manifest_path,
            "validation": dict(self.validation),
            "reports": dict(self.reports),
            "scientific_scope": DATASET_FACTORY_SCOPE,
        }


class DatasetFactory:
    """Build reusable datasets from completed simulation campaign artifacts."""

    def __init__(self, config: DatasetFactoryConfig) -> None:
        if not config.dataset_id:
            raise ValueError("dataset_id is required.")
        unsupported = sorted(set(config.export_formats) - set(DATASET_EXPORT_FORMATS))
        if unsupported:
            raise ValueError(f"unsupported dataset export formats: {unsupported}")
        self.config = config

    def discover_campaigns(self) -> tuple[Path, ...]:
        """Return source roots that exist."""

        return tuple(Path(root) for root in self.config.source_roots if Path(root).exists())

    def index_rollouts(self) -> tuple[RolloutIndexEntry, ...]:
        """Discover rollout/report JSON files and build an index."""

        entries: list[RolloutIndexEntry] = []
        for root in self.discover_campaigns():
            for path in sorted(root.rglob("*.json")):
                if _skip_json(path):
                    continue
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    continue
                if not _looks_like_rollout_result(data):
                    continue
                entries.append(_index_entry(root, path, data))
        return tuple(entries)

    def assemble_dataset(self, *, deduplicate: bool = True) -> BehaviorDataset:
        """Assemble a dataset from discovered campaign results."""

        results = [_load_result(entry.path) for entry in self.index_rollouts()]
        dataset = CampaignDatasetBuilder(
            self.config.dataset_id,
            version=self.config.dataset_version,
            metadata={
                "source_roots": list(self.config.source_roots),
                "scientific_scope": DATASET_FACTORY_SCOPE,
                **dict(self.config.metadata),
            },
        ).build(results)
        return deduplicate_dataset(dataset) if deduplicate else dataset

    def build(self, *, force: bool = False, deduplicate: bool = True) -> DatasetFactoryResult:
        """Build, export, validate, and report a dataset package."""

        output = Path(self.config.output_dir) / self.config.dataset_id
        output.mkdir(parents=True, exist_ok=True)
        index = self.index_rollouts()
        input_hash = stable_hash([entry.as_dict() for entry in index])
        cache_path = output / "dataset_factory_cache.json"
        if not force and _cache_valid(cache_path, input_hash):
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
            return DatasetFactoryResult(
                dataset_id=self.config.dataset_id,
                dataset_version=self.config.dataset_version,
                sample_count=int(cache["sample_count"]),
                cache_hit=True,
                files=dict(cache["files"]),
                manifest_path=str(cache["manifest_path"]),
                validation=dict(cache["validation"]),
                reports=dict(cache["reports"]),
            )
        dataset = self.assemble_dataset(deduplicate=deduplicate)
        files = export_dataset(dataset, output, formats=self.config.export_formats)
        manifest = create_dataset_manifest(dataset)
        manifest_path = output / "dataset_manifest.json"
        manifest_path.write_text(json.dumps(manifest.as_dict(), indent=2, sort_keys=True), encoding="utf-8")
        reports = write_dataset_reports(dataset, output_dir=output, split_ratios=self.config.split_ratios)
        validation = validate_dataset_factory_output(dataset, manifest_path=manifest_path, files=files)
        result = DatasetFactoryResult(
            dataset_id=dataset.dataset_id,
            dataset_version=dataset.version,
            sample_count=len(dataset.samples),
            cache_hit=False,
            files={key: path.as_posix() for key, path in files.items()},
            manifest_path=manifest_path.as_posix(),
            validation=validation,
            reports={key: path.as_posix() for key, path in reports.items()},
        )
        cache_path.write_text(
            json.dumps({**result.as_dict(), "input_hash": input_hash, "built_at": utc_timestamp()}, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return result


def export_dataset(dataset: BehaviorDataset, output_dir: str | Path, *, formats: Sequence[str]) -> dict[str, Path]:
    """Export a dataset in all requested formats."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    files: dict[str, Path] = {}
    for fmt in formats:
        normalized = fmt.lower()
        if normalized == "hdf5":
            files["hdf5"] = _write_hdf5(dataset, output / f"{dataset.dataset_id}.h5")
        else:
            files[normalized] = DatasetExporter.export(dataset, output / f"{dataset.dataset_id}.{normalized}", format=normalized)
    return files


def deduplicate_dataset(dataset: BehaviorDataset) -> BehaviorDataset:
    """Deduplicate samples by sample ID and sample checksum."""

    seen_ids: set[str] = set()
    seen_hashes: set[str] = set()
    samples: list[BehaviorSample] = []
    for sample in dataset.samples:
        checksum = stable_hash(sample.as_dict())
        if sample.sample_id in seen_ids or checksum in seen_hashes:
            continue
        seen_ids.add(sample.sample_id)
        seen_hashes.add(checksum)
        samples.append(sample)
    return BehaviorDataset(
        dataset_id=dataset.dataset_id,
        version=dataset.version,
        samples=tuple(samples),
        metadata={**dict(dataset.metadata), "deduplicated": True},
    )


def split_dataset(
    dataset: BehaviorDataset,
    ratios: Mapping[str, float],
) -> dict[str, tuple[str, ...]]:
    """Create deterministic train/validation/test partitions by sample ID."""

    if not ratios:
        raise ValueError("split ratios are required.")
    total_ratio = sum(float(value) for value in ratios.values())
    if total_ratio <= 0:
        raise ValueError("split ratios must sum to a positive value.")
    ids = sorted(sample.sample_id for sample in dataset.samples)
    ordered = sorted(ids, key=lambda sample_id: stable_hash(sample_id))
    splits = {name: [] for name in ratios}
    cumulative = 0
    names = list(ratios)
    for index, name in enumerate(names):
        if index == len(names) - 1:
            selected = ordered[cumulative:]
        else:
            count = int(round(len(ordered) * float(ratios[name]) / total_ratio))
            selected = ordered[cumulative : cumulative + count]
            cumulative += count
        splits[name] = selected
    return {name: tuple(values) for name, values in splits.items()}


def merge_datasets(datasets: Sequence[BehaviorDataset], *, dataset_id: str, version: str) -> BehaviorDataset:
    """Merge datasets using the existing campaign dataset merge helper."""

    return merge_campaign_datasets(datasets, dataset_id=dataset_id, version=version)


def incremental_update_dataset(existing: BehaviorDataset, additions: BehaviorDataset) -> BehaviorDataset:
    """Append new samples while preserving existing samples and deduplicating."""

    merged = BehaviorDataset(
        dataset_id=existing.dataset_id,
        version=existing.version,
        samples=tuple(existing.samples) + tuple(additions.samples),
        metadata={**dict(existing.metadata), "incremental_update": True},
    )
    return deduplicate_dataset(merged)


def dataset_statistics(dataset: BehaviorDataset) -> dict[str, Any]:
    """Generate dataset statistics and feature summaries."""

    if not dataset.samples:
        feature_report = _empty_feature_report(dataset)
    else:
        try:
            feature_report = generate_feature_matrix(dataset)
        except ValueError:
            feature_report = _feature_report_from_metadata(dataset)
    matrix = np.asarray(feature_report["matrix"], dtype=float)
    summary = {}
    for index, name in enumerate(feature_report["feature_names"]):
        column = matrix[:, index] if matrix.size else np.zeros(0, dtype=float)
        summary[name] = {
            "mean": float(np.mean(column)) if column.size else 0.0,
            "std": float(np.std(column)) if column.size else 0.0,
            "min": float(np.min(column)) if column.size else 0.0,
            "max": float(np.max(column)) if column.size else 0.0,
        }
    return {
        "dataset_id": dataset.dataset_id,
        "sample_count": len(dataset.samples),
        "conditions": sorted({sample.condition for sample in dataset.samples}),
        "feature_count": len(feature_report["feature_names"]),
        "feature_names": feature_report["feature_names"],
        "feature_summary": summary,
        "features_finite": bool(feature_report["finite"]),
    }


def coverage_report(dataset: BehaviorDataset) -> dict[str, Any]:
    """Report condition, label, and array coverage."""

    conditions: dict[str, int] = {}
    labels: dict[str, int] = {}
    arrays: dict[str, int] = {}
    for sample in dataset.samples:
        conditions[sample.condition] = conditions.get(sample.condition, 0) + 1
        for label in sample.labels:
            labels[label] = labels.get(label, 0) + 1
        for name in sample.arrays:
            arrays[name] = arrays.get(name, 0) + 1
    return {
        "condition_counts": dict(sorted(conditions.items())),
        "label_counts": dict(sorted(labels.items())),
        "array_coverage": dict(sorted(arrays.items())),
        "sample_count": len(dataset.samples),
    }


def missing_data_report(dataset: BehaviorDataset) -> dict[str, Any]:
    """Report missing arrays relative to the union of dataset array names."""

    expected = sorted({name for sample in dataset.samples for name in sample.arrays})
    rows = []
    for sample in dataset.samples:
        missing = [name for name in expected if name not in sample.arrays]
        rows.append({"sample_id": sample.sample_id, "missing_arrays": missing, "missing_count": len(missing)})
    return {"expected_arrays": expected, "samples": rows, "overall_pass": all(row["missing_count"] == 0 for row in rows)}


def quality_report(dataset: BehaviorDataset) -> dict[str, Any]:
    """Report finite arrays, duplicate IDs, missing data, and feature quality."""

    duplicate_ids = len({sample.sample_id for sample in dataset.samples}) != len(dataset.samples)
    finite_arrays = all(_sample_arrays_finite(sample) for sample in dataset.samples)
    missing = missing_data_report(dataset)
    stats = dataset_statistics(dataset)
    return {
        "duplicate_sample_ids": duplicate_ids,
        "finite_arrays": finite_arrays,
        "missing_data": missing,
        "features_finite": stats["features_finite"],
        "overall_pass": (not duplicate_ids) and finite_arrays and stats["features_finite"],
    }


def write_dataset_reports(
    dataset: BehaviorDataset,
    *,
    output_dir: str | Path,
    split_ratios: Mapping[str, float],
) -> dict[str, Path]:
    """Write statistics, metadata, feature, coverage, quality, missing-data, and card reports."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    reports = {
        "statistics": output / "dataset_statistics.json",
        "metadata": output / "dataset_metadata.json",
        "features": output / "feature_summary.json",
        "coverage": output / "coverage_report.json",
        "quality": output / "quality_report.json",
        "missing_data": output / "missing_data_report.json",
        "splits": output / "dataset_splits.json",
        "card": output / "README.md",
    }
    stats = dataset_statistics(dataset)
    coverage = coverage_report(dataset)
    missing = missing_data_report(dataset)
    quality = quality_report(dataset)
    splits = split_dataset(dataset, split_ratios)
    payloads = {
        reports["statistics"]: stats,
        reports["metadata"]: {"dataset": dataset.as_dict(), "scientific_scope": DATASET_FACTORY_SCOPE},
        reports["features"]: {"feature_names": stats["feature_names"], "feature_summary": stats["feature_summary"]},
        reports["coverage"]: coverage,
        reports["quality"]: quality,
        reports["missing_data"]: missing,
        reports["splits"]: {key: list(value) for key, value in splits.items()},
    }
    for path, payload in payloads.items():
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    reports["card"].write_text(render_dataset_card(dataset, stats=stats, coverage=coverage, quality=quality), encoding="utf-8")
    return reports


def render_dataset_card(
    dataset: BehaviorDataset,
    *,
    stats: Mapping[str, Any] | None = None,
    coverage: Mapping[str, Any] | None = None,
    quality: Mapping[str, Any] | None = None,
) -> str:
    """Render a HuggingFace-style dataset card."""

    stats = stats or dataset_statistics(dataset)
    coverage = coverage or coverage_report(dataset)
    quality = quality or quality_report(dataset)
    return (
        f"# Dataset Card: {dataset.dataset_id}\n\n"
        "## Purpose\n\n"
        "Reusable Version 2 computational locomotion dataset for repository workflows.\n\n"
        "## Generation\n\n"
        "Generated from completed simulation campaign outputs or clearly labeled synthetic demonstration data.\n\n"
        "## Dataset Summary\n\n"
        f"- Version: `{dataset.version}`\n"
        f"- Samples: {len(dataset.samples)}\n"
        f"- Conditions: `{stats['conditions']}`\n"
        f"- Feature count: {stats['feature_count']}\n\n"
        "## Coverage\n\n"
        f"`{coverage['condition_counts']}`\n\n"
        "## Quality\n\n"
        f"- Overall pass: `{quality['overall_pass']}`\n"
        f"- Finite arrays: `{quality['finite_arrays']}`\n"
        f"- Features finite: `{quality['features_finite']}`\n\n"
        "## Scientific Scope\n\n"
        f"{DATASET_FACTORY_SCOPE}\n\n"
        "## Limitations\n\n"
        "Dataset contents are computational outputs or synthetic examples. They are not direct evidence from real flies.\n\n"
        "## License\n\n"
        "MIT, matching the repository license.\n\n"
        "## Citation\n\n"
        "Cite the GitHub repository, Release v1.0.0 where relevant, and any future dataset release DOI only when one exists.\n"
    )


def validate_dataset_factory_output(
    dataset: BehaviorDataset,
    *,
    manifest_path: str | Path,
    files: Mapping[str, Path],
) -> dict[str, Any]:
    """Validate dataset consistency, manifest integrity, and exported files."""

    manifest_data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    manifest = create_dataset_manifest(dataset)
    exported = {key: path.is_file() and path.stat().st_size > 0 for key, path in files.items()}
    return {
        "dataset": validate_campaign_dataset(dataset),
        "manifest_matches": verify_dataset_integrity(dataset, manifest),
        "manifest_path_matches": dict(manifest_data.get("checksums", {})) == dict(manifest.checksums),
        "exported_files": exported,
        "quality": quality_report(dataset),
        "overall_pass": all(exported.values())
        and verify_dataset_integrity(dataset, manifest)
        and dict(manifest_data.get("checksums", {})) == dict(manifest.checksums)
        and quality_report(dataset)["overall_pass"],
    }


def synthetic_demo_dataset(*, dataset_id: str = "synthetic_dataset_factory_demo") -> BehaviorDataset:
    """Create a clearly labeled synthetic dataset for documentation and tests."""

    dataset = synthetic_behavior_dataset(dataset_id=dataset_id, sample_count=6, sample_length=24)
    samples = tuple(
        BehaviorSample(
            sample_id=f"{dataset_id}_{sample.sample_id}",
            condition=sample.condition,
            arrays=sample.arrays,
            labels=sample.labels,
            metadata=sample.metadata,
        )
        for sample in dataset.samples
    )
    return BehaviorDataset(
        dataset_id=dataset.dataset_id,
        version="synthetic_demo.v2",
        samples=samples,
        metadata={**dict(dataset.metadata), "synthetic": True, "scientific_evidence": False, "dataset_factory_demo": True},
    )


def load_dataset(path: str | Path, *, format: str | None = None) -> BehaviorDataset:
    """Load a dataset from supported factory formats."""

    source = Path(path)
    fmt = (format or source.suffix.lstrip(".")).lower()
    if fmt in {"h5", "hdf5"}:
        return _read_hdf5(source)
    return DatasetLoader.load(source, format=fmt)


def _load_result(path: str | Path) -> Mapping[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _skip_json(path: Path) -> bool:
    name = path.name.lower()
    return "manifest" in name or "checkpoint" in name or "cache" in name or "validation" in name


def _looks_like_rollout_result(data: Mapping[str, Any]) -> bool:
    return any(key in data for key in ("experiment", "plan", "arrays", "metrics", "thorax_positions", "condition"))


def _index_entry(root: Path, path: Path, data: Mapping[str, Any]) -> RolloutIndexEntry:
    experiment = data.get("experiment", data.get("plan", {}))
    sample_id = str(data.get("sample_id") or experiment.get("experiment_id") or path.stem)
    condition = str(data.get("condition") or experiment.get("role") or data.get("condition_id") or "Unknown")
    campaign_id = str(experiment.get("campaign_id") or _campaign_id_from_path(root, path))
    return RolloutIndexEntry(
        path=path.as_posix(),
        sha256=file_sha256(path),
        campaign_id=campaign_id,
        sample_id=sample_id,
        condition=condition,
        has_arrays=bool(data.get("arrays") or "thorax_positions" in data),
        has_metrics=bool(data.get("metrics")),
    )


def _campaign_id_from_path(root: Path, path: Path) -> str:
    try:
        relative = path.relative_to(root)
        return relative.parts[0] if len(relative.parts) > 1 else root.name
    except ValueError:
        return root.name


def _sample_arrays_finite(sample: BehaviorSample) -> bool:
    for value in sample.arrays.values():
        try:
            array = np.asarray(value, dtype=float)
        except (TypeError, ValueError):
            continue
        if array.size and not np.isfinite(array).all():
            return False
    return True


def _empty_feature_report(dataset: BehaviorDataset) -> dict[str, Any]:
    return {"dataset_id": dataset.dataset_id, "sample_ids": [], "conditions": [], "feature_names": [], "matrix": [], "finite": True}


def _feature_report_from_metadata(dataset: BehaviorDataset) -> dict[str, Any]:
    names = sorted(
        {
            key
            for sample in dataset.samples
            for key, value in dict(sample.metadata.get("metrics", {})).items()
            if isinstance(value, (int, float))
        }
    )
    matrix = [
        [float(dict(sample.metadata.get("metrics", {})).get(name, 0.0)) for name in names]
        for sample in dataset.samples
    ]
    values = np.asarray(matrix, dtype=float) if names else np.zeros((len(dataset.samples), 0), dtype=float)
    return {
        "dataset_id": dataset.dataset_id,
        "sample_ids": [sample.sample_id for sample in dataset.samples],
        "conditions": [sample.condition for sample in dataset.samples],
        "feature_names": names,
        "matrix": values.tolist(),
        "finite": bool(np.isfinite(values).all()),
    }


def _cache_valid(path: Path, input_hash: str) -> bool:
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    files = data.get("files", {})
    return data.get("input_hash") == input_hash and all(Path(value).is_file() for value in files.values())


def _write_hdf5(dataset: BehaviorDataset, path: Path) -> Path:
    try:
        import h5py
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("h5py is required for HDF5 dataset export.") from exc
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as handle:  # pragma: no cover - optional dependency
        handle.attrs["dataset_json"] = json.dumps(dataset.as_dict(), sort_keys=True)
        for sample in dataset.samples:
            group = handle.create_group(sample.sample_id)
            group.attrs["condition"] = sample.condition
            for name, value in sample.arrays.items():
                try:
                    group.create_dataset(name, data=np.asarray(value, dtype=float))
                except (TypeError, ValueError):
                    group.attrs[f"{name}_json"] = json.dumps(value, sort_keys=True)
    return path


def _read_hdf5(path: Path) -> BehaviorDataset:
    try:
        import h5py
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("h5py is required for HDF5 dataset loading.") from exc
    with h5py.File(path, "r") as handle:  # pragma: no cover - optional dependency
        return BehaviorDataset.from_dict(json.loads(handle.attrs["dataset_json"]))


__all__ = [
    "DATASET_EXPORT_FORMATS",
    "DATASET_FACTORY_SCOPE",
    "DatasetFactory",
    "DatasetFactoryConfig",
    "DatasetFactoryResult",
    "RolloutIndexEntry",
    "coverage_report",
    "dataset_statistics",
    "deduplicate_dataset",
    "export_dataset",
    "incremental_update_dataset",
    "load_dataset",
    "merge_datasets",
    "missing_data_report",
    "quality_report",
    "render_dataset_card",
    "split_dataset",
    "synthetic_demo_dataset",
    "validate_dataset_factory_output",
    "write_dataset_reports",
]
