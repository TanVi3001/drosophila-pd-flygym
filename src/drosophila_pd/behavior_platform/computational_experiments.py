"""Canonical computational experiment definitions and reports for v2."""

from __future__ import annotations

import html
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from drosophila_pd.behavior_platform.campaign_provenance import file_sha256, stable_hash
from drosophila_pd.behavior_platform.campaign_reproducibility import verify_artifact_hashes


EXPERIMENT_SCOPE = (
    "Version 2 computational experiment definition only; no biological "
    "validation, diagnosis, disease-severity mapping, dopamine equivalence, "
    "or mechanistic claim."
)

EXPERIMENT_REPORT_FORMATS = ("markdown", "html", "json")
EXPERIMENT_TEMPLATE_TYPES = (
    "single_experiment",
    "parameter_sweep",
    "robustness_study",
    "progression_study",
    "intervention_study",
    "benchmark_study",
)


@dataclass(frozen=True)
class ExperimentDefinition:
    """One canonical v2 computational experiment definition."""

    experiment_id: str
    display_name: str
    experiment_type: str
    campaign_id: str
    metadata: Mapping[str, Any]
    parameters: Mapping[str, Any]
    random_seeds: tuple[int, ...]
    provenance: Mapping[str, Any]
    expected_outputs: tuple[str, ...]
    configuration_hash: str
    version: str = "v2.experiment.1"

    def __post_init__(self) -> None:
        if self.experiment_type not in EXPERIMENT_TEMPLATE_TYPES:
            raise ValueError(f"unsupported experiment_type: {self.experiment_type}")
        if not self.random_seeds:
            raise ValueError("random_seeds must not be empty.")

    def hash_payload(self) -> dict[str, Any]:
        return {
            "experiment_definition_version": self.version,
            "experiment_id": self.experiment_id,
            "display_name": self.display_name,
            "experiment_type": self.experiment_type,
            "campaign_id": self.campaign_id,
            "metadata": dict(self.metadata),
            "parameters": dict(self.parameters),
            "random_seeds": [int(seed) for seed in self.random_seeds],
            "provenance": dict(self.provenance),
            "expected_outputs": list(self.expected_outputs),
        }

    def hash_valid(self) -> bool:
        return self.configuration_hash == stable_hash(self.hash_payload())

    def as_dict(self) -> dict[str, Any]:
        return {
            **self.hash_payload(),
            "configuration_hash": self.configuration_hash,
            "hash_valid": self.hash_valid(),
            "scientific_scope": EXPERIMENT_SCOPE,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ExperimentDefinition":
        return cls(
            experiment_id=str(data["experiment_id"]),
            display_name=str(data["display_name"]),
            experiment_type=str(data["experiment_type"]),
            campaign_id=str(data["campaign_id"]),
            metadata=dict(data.get("metadata", {})),
            parameters=dict(data.get("parameters", {})),
            random_seeds=tuple(int(seed) for seed in data.get("random_seeds", ())),
            provenance=dict(data.get("provenance", {})),
            expected_outputs=tuple(data.get("expected_outputs", ())),
            configuration_hash=str(data["configuration_hash"]),
            version=str(data.get("experiment_definition_version", "v2.experiment.1")),
        )


@dataclass(frozen=True)
class CampaignTemplate:
    """Reusable deterministic campaign template."""

    template_id: str
    template_type: str
    description: str
    required_fields: tuple[str, ...]
    deterministic: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)
    version: str = "v2.experiment_template.1"

    def as_dict(self) -> dict[str, Any]:
        return {
            "campaign_template_version": self.version,
            "template_id": self.template_id,
            "template_type": self.template_type,
            "description": self.description,
            "required_fields": list(self.required_fields),
            "deterministic": bool(self.deterministic),
            "metadata": dict(self.metadata),
            "scientific_scope": EXPERIMENT_SCOPE,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CampaignTemplate":
        return cls(
            template_id=str(data["template_id"]),
            template_type=str(data["template_type"]),
            description=str(data["description"]),
            required_fields=tuple(data.get("required_fields", ())),
            deterministic=bool(data.get("deterministic", True)),
            metadata=dict(data.get("metadata", {})),
            version=str(data.get("campaign_template_version", "v2.experiment_template.1")),
        )


def load_experiment_definition(path: str | Path) -> ExperimentDefinition:
    """Load and validate a canonical experiment definition."""

    definition = ExperimentDefinition.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
    if not definition.hash_valid():
        raise ValueError(f"configuration_hash mismatch for {path}")
    return definition


def load_experiment_library(root: str | Path) -> tuple[ExperimentDefinition, ...]:
    """Load all experiment definitions under a directory."""

    return tuple(load_experiment_definition(path) for path in sorted(Path(root).glob("*.json")))


def load_campaign_templates(root: str | Path) -> tuple[CampaignTemplate, ...]:
    """Load reusable campaign templates."""

    return tuple(
        CampaignTemplate.from_dict(json.loads(path.read_text(encoding="utf-8")))
        for path in sorted(Path(root).glob("*.json"))
    )


def validate_experiment_definition(definition: ExperimentDefinition) -> dict[str, Any]:
    """Validate schema, hash, provenance, seeds, and expected outputs."""

    checks = {
        "schema": bool(definition.experiment_id and definition.display_name and definition.campaign_id),
        "hash": definition.hash_valid(),
        "provenance": bool(definition.provenance.get("source")),
        "seeds": len(definition.random_seeds) > 0 and len(set(definition.random_seeds)) == len(definition.random_seeds),
        "expected_outputs": len(definition.expected_outputs) > 0,
        "scientific_scope": definition.metadata.get("biological_claims") is False,
    }
    return {
        "experiment_id": definition.experiment_id,
        "checks": checks,
        "overall_pass": all(checks.values()),
    }


def validate_experiment_library(root: str | Path) -> dict[str, Any]:
    """Validate a complete experiment definition library."""

    definitions = load_experiment_library(root)
    rows = [validate_experiment_definition(definition) for definition in definitions]
    return {
        "experiment_library_version": 2,
        "experiment_count": len(definitions),
        "experiments": rows,
        "overall_pass": all(row["overall_pass"] for row in rows),
        "scientific_scope": EXPERIMENT_SCOPE,
    }


def render_experiment_report(
    definition: ExperimentDefinition,
    *,
    descriptive_statistics: Mapping[str, Any] | None = None,
    generated_artifacts: Mapping[str, str | Path] | None = None,
    output_dir: str | Path,
    formats: Sequence[str] = EXPERIMENT_REPORT_FORMATS,
) -> dict[str, Path]:
    """Render Markdown, HTML, and JSON reports for an experiment."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    normalized = tuple(fmt.lower() for fmt in formats)
    unsupported = sorted(set(normalized) - set(EXPERIMENT_REPORT_FORMATS))
    if unsupported:
        raise ValueError(f"unsupported experiment report formats: {unsupported}")
    artifacts = {key: Path(path).as_posix() for key, path in (generated_artifacts or {}).items()}
    payload = {
        "experiment_report_version": 2,
        "definition": definition.as_dict(),
        "descriptive_statistics": dict(descriptive_statistics or {}),
        "generated_artifacts": artifacts,
        "integrity_verification": verify_generated_artifacts(artifacts),
        "scientific_scope": EXPERIMENT_SCOPE,
    }
    files: dict[str, Path] = {}
    if "json" in normalized:
        files["json"] = output / f"{definition.experiment_id}_report.json"
        files["json"].write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if "markdown" in normalized:
        files["markdown"] = output / f"{definition.experiment_id}_report.md"
        files["markdown"].write_text(_markdown_report(payload), encoding="utf-8")
    if "html" in normalized:
        files["html"] = output / f"{definition.experiment_id}_report.html"
        files["html"].write_text(_html_report(payload), encoding="utf-8")
    return files


def build_campaign_dashboard(
    *,
    completed: Sequence[str],
    pending: Sequence[str],
    failed: Sequence[str],
    dataset_checks: Mapping[str, bool],
    artifact_checks: Mapping[str, bool],
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Build a campaign progress and completeness dashboard payload."""

    total = len(completed) + len(pending) + len(failed)
    payload = {
        "dashboard_version": 2,
        "completed_experiments": list(completed),
        "pending_experiments": list(pending),
        "failed_experiments": list(failed),
        "campaign_progress": {
            "total": total,
            "completed": len(completed),
            "pending": len(pending),
            "failed": len(failed),
            "completion_fraction": len(completed) / total if total else 1.0,
        },
        "dataset_completeness": dict(dataset_checks),
        "artifact_completeness": dict(artifact_checks),
        "overall_pass": not failed and all(dataset_checks.values()) and all(artifact_checks.values()),
        "scientific_scope": EXPERIMENT_SCOPE,
    }
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def verify_generated_artifacts(artifacts: Mapping[str, str | Path]) -> dict[str, Any]:
    """Verify generated artifact existence and hashes."""

    manifest = {
        "artifacts": {
            key: {"path": Path(path).as_posix(), "sha256": file_sha256(path)}
            for key, path in artifacts.items()
            if Path(path).is_file()
        }
    }
    missing = [key for key, path in artifacts.items() if not Path(path).is_file()]
    report = verify_artifact_hashes(manifest) if manifest["artifacts"] else {"overall_pass": not missing, "artifacts": []}
    return {**report, "missing": missing, "overall_pass": report["overall_pass"] and not missing}


def _markdown_report(payload: Mapping[str, Any]) -> str:
    definition = payload["definition"]
    stats = payload["descriptive_statistics"]
    artifacts = payload["generated_artifacts"]
    lines = [
        f"# {definition['display_name']}",
        "",
        payload["scientific_scope"],
        "",
        f"- Experiment ID: `{definition['experiment_id']}`",
        f"- Type: `{definition['experiment_type']}`",
        f"- Campaign ID: `{definition['campaign_id']}`",
        f"- Configuration hash: `{definition['configuration_hash']}`",
        f"- Random seeds: `{definition['random_seeds']}`",
        f"- Artifact count: {len(artifacts)}",
        f"- Statistic groups: {len(stats)}",
        "",
    ]
    return "\n".join(lines)


def _html_report(payload: Mapping[str, Any]) -> str:
    definition = payload["definition"]
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>{html.escape(definition['display_name'])}</title></head><body>"
        f"<h1>{html.escape(definition['display_name'])}</h1>"
        f"<p>{html.escape(payload['scientific_scope'])}</p>"
        f"<pre>{html.escape(json.dumps(payload, indent=2, sort_keys=True))}</pre>"
        "</body></html>"
    )


__all__ = [
    "EXPERIMENT_REPORT_FORMATS",
    "EXPERIMENT_SCOPE",
    "EXPERIMENT_TEMPLATE_TYPES",
    "CampaignTemplate",
    "ExperimentDefinition",
    "build_campaign_dashboard",
    "load_campaign_templates",
    "load_experiment_definition",
    "load_experiment_library",
    "render_experiment_report",
    "validate_experiment_definition",
    "validate_experiment_library",
    "verify_generated_artifacts",
]
