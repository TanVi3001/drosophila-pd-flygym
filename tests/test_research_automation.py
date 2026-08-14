"""Tests for metadata-only Milestone 3 automation services."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from drosophila_pd.automation import (
    ArtifactManager,
    BenchmarkCenter,
    DatasetCatalog,
    DeveloperToolkit,
    ExperimentQueueManager,
    ProjectHealthMonitor,
    PublicationBuilder,
    ReproducibilityCenter,
    ResearchAutomationPlatform,
)
from drosophila_pd.experiment import ExperimentJob, STAGE_NAMES

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from research_automation_cli import main  # noqa: E402


def _handlers():
    return {stage: (lambda context, stage=stage: {"stage": stage, "job_id": context["job"].job_id}) for stage in STAGE_NAMES}


def test_dataset_catalog_versions_search_and_integrity(tmp_path):
    source = tmp_path / "rollout.json"
    source.write_text('{"source":"caller"}', encoding="utf-8")
    catalog = DatasetCatalog(tmp_path / "catalog")
    entry = catalog.add(source, dataset_id="healthy-001", name="healthy", version_name="v1", tags=("adult",), species="Drosophila")

    assert catalog.get(entry.dataset_id).sha256
    assert [item.dataset_id for item in catalog.search("adult")] == ["healthy-001"]
    assert len(catalog.versions("healthy")) == 1
    assert catalog.verify()["overall_pass"] is True
    loaded = DatasetCatalog.load(tmp_path / "catalog" / "dataset_catalog.json")
    assert loaded.verify()["overall_pass"] is True
    source.write_text('{"source":"changed"}', encoding="utf-8")
    assert loaded.verify()["overall_pass"] is False


def test_experiment_queue_manager_persists_progress_and_cancel(tmp_path):
    manager = ExperimentQueueManager(tmp_path / "queue")
    job = ExperimentJob("job-a", {"seed": 0}, tmp_path / "runs")
    manager.enqueue(job)
    results = manager.run(stage_handlers=_handlers())

    assert results[0].status.value == "COMPLETED"
    assert manager.status()["counts"]["COMPLETED"] == 1
    assert manager.state_path.is_file()
    loaded = ExperimentQueueManager.load(manager.state_path)
    assert loaded.status()["counts"]["COMPLETED"] == 1

    cancelled = loaded.enqueue(ExperimentJob("job-b", {}, tmp_path / "runs"))
    loaded.cancel(cancelled.job_id)
    assert cancelled.status.value == "CANCELLED"


def test_reproducibility_artifact_publication_and_benchmark_services(tmp_path):
    source = tmp_path / "input.json"
    source.write_text("{}", encoding="utf-8")
    repro = ReproducibilityCenter(Path(__file__).parents[1])
    manifest = repro.collect(campaign_id="test", configuration={"seed": 0}, dataset_paths=[source], seeds=[0])
    assert manifest["configuration_hash"]
    assert repro.verify(manifest)["overall_pass"] is True

    artifacts = ArtifactManager(tmp_path / "artifacts")
    artifacts.prepare()
    artifacts.register_file(source, "json")
    artifact_manifest = artifacts.write_manifest()
    assert artifact_manifest.is_file()
    assert artifacts.verify()["overall_pass"] is True

    publication = PublicationBuilder(tmp_path / "publication")
    target = publication.register(source, "metadata")
    assert target.is_file()
    assert publication.build().is_file()

    benchmark = BenchmarkCenter()
    benchmark.register("Import", lambda: source.read_text(encoding="utf-8"))
    assert benchmark.run()["complete"] is True
    assert benchmark.not_run_report()["status"] == "not_run"


def test_health_toolkit_platform_and_cli_are_non_simulation(tmp_path):
    root = Path(__file__).parents[1]
    health = ProjectHealthMonitor(root).run()
    assert health["overall_pass"] is True
    toolkit = DeveloperToolkit(root)
    assert toolkit.api_report()["module_count"] > 0
    assert toolkit.dependency_report()["nodes"]
    assert toolkit.test_report()["test_count"] > 0

    platform = ResearchAutomationPlatform(root, tmp_path / "outputs")
    output = platform.write_manifest()
    assert json.loads(output.read_text(encoding="utf-8"))["scientific_scope"]
    assert main(["--root", str(root), "health-check"]) == 0
