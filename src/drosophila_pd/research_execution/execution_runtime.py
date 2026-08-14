"""Dataset-gated orchestration for the V6 campaign execution workflow."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

try:
    import yaml
except ImportError:  # pragma: no cover - declared runtime dependency
    yaml = None

from drosophila_pd.research_pipeline import DatasetInput, StudyOrchestrator, StudyRequest
from drosophila_pd.research_campaign import Campaign

from .artifact_registry import ArtifactRegistry
from .execution_context import ExecutionContext
from .execution_history import ExecutionHistory
from .execution_result import ExecutionResult
from .execution_state import ExecutionState


EXECUTION_STAGES = (
    "dataset",
    "campaign",
    "study_orchestrator",
    "analysis",
    "statistics",
    "computational_pd",
    "scientific_validation",
    "publication",
    "research_package",
)
PLANNING_STATUSES = {"PLANNING_ONLY", "PLANNED", "RESERVED_FOR_EXECUTION"}
MANIFEST_NAMES = {
    "manifest.json",
    "dataset_manifest.json",
    "manifest.yaml",
    "manifest.yml",
    "dataset_manifest.yaml",
    "dataset_manifest.yml",
}


@dataclass
class DatasetRecord:
    """Manifest-level dataset metadata; rollout contents are never parsed."""

    dataset_id: str
    root: Path
    manifest_path: Path
    manifest: Mapping[str, Any]
    metadata_path: Path | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    checksum_path: Path | None = None
    checksums: Mapping[str, Any] = field(default_factory=dict)
    payload_paths: tuple[Path, ...] = ()
    missing_paths: tuple[Path, ...] = ()
    status: str = "WAITING_DATASET"
    reason: str = ""

    @property
    def ready(self) -> bool:
        return self.status == "READY"

    def as_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "root": self.root.as_posix(),
            "manifest": self.manifest_path.as_posix(),
            "metadata": self.metadata_path.as_posix() if self.metadata_path else None,
            "checksum": self.checksum_path.as_posix() if self.checksum_path else None,
            "payload_paths": [path.as_posix() for path in self.payload_paths],
            "missing_paths": [path.as_posix() for path in self.missing_paths],
            "status": self.status,
            "reason": self.reason,
        }


@dataclass
class DiscoveryReport:
    """Result of manifest-only dataset discovery."""

    state: ExecutionState
    datasets: list[DatasetRecord]
    searched_roots: tuple[Path, ...]
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "state": self.state.value,
            "datasets": [dataset.as_dict() for dataset in self.datasets],
            "searched_roots": [path.as_posix() for path in self.searched_roots],
            "warnings": list(self.warnings),
            "rollout_parsing": "not performed",
        }


DatasetRunner = Callable[[StudyRequest, Path, Path], Any]


class DatasetDiscovery:
    """Discover executable dataset manifests without reading rollout arrays."""

    def discover(self, roots: Sequence[str | Path]) -> DiscoveryReport:
        resolved_roots = tuple(Path(root).resolve() for root in roots)
        manifests = []
        for root in resolved_roots:
            if not root.exists():
                continue
            candidates = [root] if root.is_file() else sorted(root.rglob("*"))
            for candidate in candidates:
                if candidate.is_file() and candidate.name in MANIFEST_NAMES:
                    manifests.append(candidate)
        datasets: list[DatasetRecord] = []
        warnings: list[str] = []
        for manifest_path in sorted(set(manifests)):
            payload = _read_structured(manifest_path)
            status = str(payload.get("status", "")).upper()
            if status in PLANNING_STATUSES or payload.get("execution_enabled") is False:
                warnings.append(f"ignored non-executable manifest: {manifest_path.as_posix()}")
                continue
            datasets.append(_record_from_manifest(manifest_path, payload))
        ready = [dataset for dataset in datasets if dataset.ready]
        if not ready:
            warnings.append("No executable dataset manifest with an available payload was found.")
        return DiscoveryReport(
            state=ExecutionState.READY if ready else ExecutionState.WAITING_DATASET,
            datasets=datasets,
            searched_roots=resolved_roots,
            warnings=warnings,
        )


class ExecutionRuntime:
    """Run or report a campaign only after real dataset payloads are present."""

    def __init__(
        self,
        context: ExecutionContext,
        *,
        study_runner: DatasetRunner | None = None,
    ) -> None:
        self.context = context
        self.study_runner = study_runner or self._default_study_runner

    def discover(self) -> DiscoveryReport:
        return DatasetDiscovery().discover(self.context.dataset_search_roots)

    def prepare(self) -> ExecutionResult:
        started = time.perf_counter()
        discovery = self.discover()
        history = ExecutionHistory()
        if discovery.state is ExecutionState.READY:
            history.transition(ExecutionState.READY, "Executable dataset manifest discovered.")
            warnings = discovery.warnings
        else:
            warnings = discovery.warnings
        result = self._result(
            history,
            discovery,
            stages=self._stage_rows(discovery.state),
            duration=time.perf_counter() - started,
            warnings=warnings,
        )
        return self._write_report(result)

    def execute(self) -> ExecutionResult:
        started = time.perf_counter()
        discovery = self.discover()
        history = ExecutionHistory()
        if discovery.state is not ExecutionState.READY:
            result = self._result(
                history,
                discovery,
                stages=self._stage_rows(ExecutionState.WAITING_DATASET),
                duration=time.perf_counter() - started,
                warnings=discovery.warnings,
            )
            return self._write_report(result)

        try:
            history.transition(ExecutionState.READY, "Executable dataset manifest discovered.")
            history.transition(ExecutionState.RUNNING, "Delegating to the existing StudyOrchestrator.")
            request = self._study_request(discovery)
            study_result = self.study_runner(request, self.context.repository_root, self.context.output_root / "study_outputs")
            history.transition(ExecutionState.VALIDATING, "Study orchestration returned validation output.")
            validation = dict(getattr(study_result, "validation", {}) or {})
            history.transition(ExecutionState.EXPORTING, "Registering existing orchestration artifacts.")
            registry = ArtifactRegistry(self.context.output_root)
            study_root = Path(getattr(study_result, "study_root", self.context.output_root / "study_outputs"))
            registry.register_tree(study_root)
            bundle = getattr(study_result, "package_path", None)
            if bundle and Path(bundle).is_file():
                registry.register(bundle, "bundle")
            history.transition(ExecutionState.COMPLETED, "Execution artifacts registered.")
            result = self._result(
                history,
                discovery,
                stages=self._stage_rows(ExecutionState.COMPLETED),
                artifacts=[record.as_dict() for record in registry.records],
                validation=validation,
                duration=time.perf_counter() - started,
                warnings=discovery.warnings,
            )
            return self._write_report(result, registry=registry)
        except Exception as error:  # pragma: no cover - exercised by caller-provided integrations
            if history.state in {ExecutionState.RUNNING, ExecutionState.VALIDATING, ExecutionState.EXPORTING}:
                history.transition(ExecutionState.FAILED, f"Execution failed: {error}")
            result = self._result(
                history,
                discovery,
                stages=self._stage_rows(ExecutionState.FAILED),
                duration=time.perf_counter() - started,
                errors=[f"{type(error).__name__}: {error}"],
                warnings=discovery.warnings,
            )
            return self._write_report(result)

    def status(self) -> dict[str, Any]:
        report = self.context.output_root / "execution_report.json"
        if report.is_file():
            return json.loads(report.read_text(encoding="utf-8"))
        return self.prepare().as_dict()

    def report(self) -> dict[str, Any]:
        return self.status()

    def bundle(self) -> dict[str, Any]:
        payload = self.status()
        bundles = [item for item in payload.get("artifacts", ()) if item.get("category") == "bundle"]
        payload["bundle"] = bundles[0] if bundles else None
        if not bundles and payload.get("state") == ExecutionState.WAITING_DATASET.value:
            payload.setdefault("warnings", []).append("Bundle not created because dataset discovery is waiting.")
        return payload

    def _default_study_runner(self, request: StudyRequest, repository_root: Path, output_root: Path) -> Any:
        return StudyOrchestrator(repository_root, output_root).run(request)

    def _study_request(self, discovery: DiscoveryReport) -> StudyRequest:
        ready = [dataset for dataset in discovery.datasets if dataset.ready]
        datasets = tuple(
            DatasetInput(source=dataset.root, dataset_id=dataset.dataset_id, metadata=dict(dataset.manifest))
            for dataset in ready
        )
        campaign_payload = _read_campaign(self.context.campaign_config_path)
        name = str(campaign_payload.get("name", self.context.campaign_id))
        campaign = Campaign(name=name, metadata=campaign_payload)
        return StudyRequest(
            study_id=self.context.campaign_id,
            name=name,
            datasets=datasets,
            campaign=campaign,
            metadata={"execution_context": self.context.as_dict(), "campaign": campaign_payload},
        )

    def _result(
        self,
        history: ExecutionHistory,
        discovery: DiscoveryReport,
        *,
        stages: list[Mapping[str, Any]],
        artifacts: list[Mapping[str, Any]] | None = None,
        validation: Mapping[str, Any] | None = None,
        duration: float = 0.0,
        errors: list[str] | None = None,
        warnings: list[str] | None = None,
    ) -> ExecutionResult:
        return ExecutionResult(
            execution_id=self.context.campaign_id,
            state=history.state,
            datasets=[dataset.as_dict() for dataset in discovery.datasets],
            stages=stages,
            artifacts=artifacts or [],
            validation=validation or {"overall_pass": False, "status": history.state.value},
            duration_seconds=duration,
            errors=errors or [],
            warnings=warnings or [],
            history=history.as_dict(),
            context=self.context.as_dict(),
        )

    def _write_report(self, result: ExecutionResult, *, registry: ArtifactRegistry | None = None) -> ExecutionResult:
        self.context.output_root.mkdir(parents=True, exist_ok=True)
        json_path = self.context.output_root / "execution_report.json"
        md_path = self.context.output_root / "execution_report.md"
        json_path.write_text(json.dumps(result.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        md_path.write_text(_markdown_report(result), encoding="utf-8")
        active_registry = registry or ArtifactRegistry(self.context.output_root)
        active_registry.register(json_path, "reports")
        active_registry.register(md_path, "reports")
        active_registry.write()
        return result

    @staticmethod
    def _stage_rows(state: ExecutionState) -> list[dict[str, str]]:
        return [{"stage": name, "status": state.value} for name in EXECUTION_STAGES]


def _record_from_manifest(manifest_path: Path, payload: Mapping[str, Any]) -> DatasetRecord:
    root = manifest_path.parent.resolve()
    entries = payload.get("entries", payload.get("payloads", payload.get("files", ())))
    payload_paths: list[Path] = []
    missing_paths: list[Path] = []
    for entry in entries if isinstance(entries, (list, tuple)) else ():
        value = entry.get("path", entry.get("source", entry.get("file"))) if isinstance(entry, Mapping) else entry
        if not value:
            continue
        candidate = Path(str(value))
        resolved = candidate if candidate.is_absolute() else root / candidate
        payload_paths.append(resolved.resolve())
        if not resolved.exists():
            missing_paths.append(resolved.resolve())
    metadata_path = _first_file(root, ("metadata.json", "metadata.yaml", "metadata.yml"))
    checksum_path = _first_file(root, ("checksum.json", "checksums.json", "checksum.yaml", "checksums.yaml"))
    metadata = _read_structured(metadata_path) if metadata_path else {}
    checksums = _read_structured(checksum_path) if checksum_path else {}
    if not payload_paths:
        status, reason = "WAITING_DATASET", "Manifest contains no payload entries."
    elif missing_paths:
        status, reason = "WAITING_DATASET", "One or more declared payload paths are missing."
    else:
        status, reason = "READY", "Manifest and declared payload paths are available."
    return DatasetRecord(
        dataset_id=str(payload.get("dataset_id", payload.get("id", root.name))),
        root=root,
        manifest_path=manifest_path.resolve(),
        manifest=payload,
        metadata_path=metadata_path,
        metadata=metadata,
        checksum_path=checksum_path,
        checksums=checksums,
        payload_paths=tuple(payload_paths),
        missing_paths=tuple(missing_paths),
        status=status,
        reason=reason,
    )


def _read_campaign(path: Path) -> dict[str, Any]:
    return _read_structured(path) if path.is_file() else {}


def _read_structured(path: Path) -> dict[str, Any]:
    try:
        if path.suffix.lower() == ".json":
            value = json.loads(path.read_text(encoding="utf-8"))
        elif yaml is not None:
            value = yaml.safe_load(path.read_text(encoding="utf-8"))
        else:  # pragma: no cover - PyYAML is a declared dependency
            return {}
    except Exception:  # malformed external metadata must leave the runtime waiting
        return {}
    return dict(value) if isinstance(value, Mapping) else {}


def _first_file(root: Path, names: Sequence[str]) -> Path | None:
    for name in names:
        candidate = root / name
        if candidate.is_file():
            return candidate
    return None


def _markdown_report(result: ExecutionResult) -> str:
    payload = result.as_dict()
    lines = [
        "# Execution Report",
        "",
        f"- Execution: `{payload['execution_id']}`",
        f"- State: `{payload['state']}`",
        f"- Duration (s): `{payload['duration_seconds']:.6f}`",
        "- Scope: execution orchestration over supplied computational datasets only.",
        "",
        "## Datasets",
        "",
        f"- Discovered: `{len(payload['datasets'])}`",
        f"- Rollout parsing: `{payload['context'].get('rollout_parsing', 'not performed')}`",
        "",
        "## Stages",
        "",
        "| Stage | Status |",
        "| --- | --- |",
    ]
    lines.extend(f"| {item['stage']} | {item['status']} |" for item in payload["stages"])
    lines.extend(["", "## Artifacts", ""])
    if payload["artifacts"]:
        lines.extend(f"- `{item['category']}`: `{item['path']}`" for item in payload["artifacts"])
    else:
        lines.append("- None registered.")
    lines.extend(["", "## Validation", "", f"```json\n{json.dumps(payload['validation'], indent=2, sort_keys=True)}\n```", ""])
    if payload["warnings"]:
        lines.extend(["## Warnings", "", *[f"- {item}" for item in payload["warnings"]], ""])
    if payload["errors"]:
        lines.extend(["## Errors", "", *[f"- {item}" for item in payload["errors"]], ""])
    return "\n".join(lines)


__all__ = ["DatasetDiscovery", "DatasetRecord", "DiscoveryReport", "EXECUTION_STAGES", "ExecutionRuntime"]
