"""Configuration models for the imported-rollout experiment suite."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Path):
        return value.as_posix()
    return value


def _as_strings(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return tuple(item.strip() for item in value.split(",") if item.strip())
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return tuple(str(item) for item in value)
    return (str(value),)


@dataclass(frozen=True)
class ExperimentConfig:
    """One declarative experiment over an already imported dataset."""

    experiment_id: str
    name: str
    condition: str
    dataset: str
    config_path: Path
    description: str = ""
    seed: int | None = None
    parameters: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    expected_outputs: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    @classmethod
    def from_file(cls, path: str | Path) -> "ExperimentConfig":
        source = Path(path).expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(f"Experiment config not found: {path}")
        payload = yaml.safe_load(source.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"Experiment config must contain a mapping: {source}")
        nested = payload.get("experiment")
        values = dict(nested) if isinstance(nested, Mapping) else dict(payload)
        identifier = values.get("experiment_id", values.get("id", source.stem))
        identifier = str(identifier)
        if not identifier or identifier in {".", ".."} or Path(identifier).name != identifier:
            raise ValueError(f"Invalid experiment id: {identifier!r}")
        dataset = values.get("dataset", values.get("dataset_path", ""))
        condition = values.get("condition", values.get("group", identifier))
        return cls(
            experiment_id=identifier,
            name=str(values.get("name", identifier)),
            condition=str(condition),
            dataset=str(dataset),
            config_path=source,
            description=str(values.get("description", "")),
            seed=_optional_int(values.get("seed")),
            parameters=dict(values.get("parameters", {})) if isinstance(values.get("parameters"), Mapping) else {},
            metadata=dict(values.get("metadata", {})) if isinstance(values.get("metadata"), Mapping) else {},
            expected_outputs=_as_strings(values.get("expected_outputs")),
            tags=_as_strings(values.get("tags")),
        )

    def dataset_path(self, repository_root: str | Path) -> Path:
        """Resolve the configured dataset without creating or mutating it."""

        root = Path(repository_root).resolve()
        configured = Path(self.dataset).expanduser() if self.dataset else Path()
        if configured.is_absolute():
            return configured.resolve()
        if self.dataset:
            direct = (root / configured).resolve()
            if direct.exists():
                return direct
            return direct
        category = self.condition.strip().lower().replace(" ", "_")
        return (root / "datasets" / category / self.experiment_id).resolve()

    def config_hash(self) -> str:
        """Return a stable hash of the YAML's parsed configuration."""

        payload = self.as_dict(include_path=False)
        encoded = json.dumps(_jsonable(payload), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def as_dict(self, *, include_path: bool = True) -> dict[str, Any]:
        payload = {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "condition": self.condition,
            "dataset": self.dataset,
            "description": self.description,
            "seed": self.seed,
            "parameters": _jsonable(self.parameters),
            "metadata": _jsonable(self.metadata),
            "expected_outputs": list(self.expected_outputs),
            "tags": list(self.tags),
        }
        if include_path:
            payload["config_path"] = self.config_path.as_posix()
        return payload


def load_experiment_configs(
    paths: Sequence[str | Path] | None = None,
    *,
    config_dir: str | Path = "experiments",
) -> tuple[ExperimentConfig, ...]:
    """Load YAML experiment definitions in deterministic path order."""

    if paths is None:
        source_dir = Path(config_dir)
        candidates = sorted((*source_dir.glob("*.yaml"), *source_dir.glob("*.yml")))
    else:
        candidates = []
        for item in paths:
            source = Path(item)
            candidates.extend(sorted(source.glob("*.yaml"))) if source.is_dir() else candidates.append(source)
    if not candidates:
        raise FileNotFoundError("No experiment YAML files were found.")
    configs = tuple(ExperimentConfig.from_file(path) for path in sorted(set(candidates), key=lambda value: str(value)))
    identifiers = [config.experiment_id for config in configs]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("Experiment ids must be unique within a suite.")
    return configs


def _optional_int(value: Any) -> int | None:
    if value in (None, "", "None"):
        return None
    return int(value)


__all__ = ["ExperimentConfig", "load_experiment_configs"]
