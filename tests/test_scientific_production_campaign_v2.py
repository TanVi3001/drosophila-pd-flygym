from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from drosophila_pd.behavior_platform import (  # noqa: E402
    PRODUCTION_OUTPUT_FOLDERS,
    SCIENTIFIC_CAMPAIGN_SCOPE,
    CampaignConfig,
    CampaignDatasetBuilder,
    CampaignExecutionStatus,
    FlyGymBatchExecutor,
    build_manuscript_assets,
    build_scientific_dataset_package,
    campaign_status,
    canonical_production_layout,
    create_campaign,
    execute_production_campaign,
    flygym_available,
    generate_scientific_figures,
    load_campaign_library,
    load_campaign_library_entry,
    recover_checkpoint,
    run_scientific_analysis,
    stable_hash,
    validate_scientific_campaign_package,
)


def _results():
    rows = []
    for index, condition in enumerate(("Healthy", "Candidate", "Progression")):
        x = np.linspace(0.0, 1.0 + index * 0.2, 10)
        y = np.sin(x + index * 0.1)
        rows.append(
            {
                "sample_id": f"sample_{index}",
                "condition": condition,
                "experiment": {"experiment_id": f"exp_{index}", "role": condition, "seed": index, "replicate": 0},
                "arrays": {
                    "thorax_positions": np.column_stack([x, y, np.ones_like(x)]).tolist(),
                    "heading": np.unwrap(np.arctan2(np.gradient(y), np.gradient(x))).tolist(),
                },
                "metrics": {
                    "mean_speed": 1.0 + index,
                    "yaw_rate_abs_mean": 0.1 + 0.01 * index,
                    "gait_score": 0.8,
                    "exploration_index": 0.6,
                    "comparison_score": 1.0 - 0.1 * index,
                    "benchmark_score": 0.9,
                    "progression_stage_index": index,
                },
            }
        )
    return rows


def test_campaign_library_entries_have_hashes_provenance_and_layout():
    entries = load_campaign_library(REPO_ROOT / "configs" / "v2" / "campaigns")
    names = {entry.campaign_name for entry in entries}
    expected = {
        "healthy_baseline",
        "pd_candidate",
        "progression_stage_0",
        "progression_stage_1",
        "progression_stage_2",
        "progression_stage_3",
        "progression_stage_4",
        "intervention_reference",
        "benchmark_suite",
    }
    assert expected <= names
    for entry in entries:
        assert entry.hash_valid()
        assert entry.configuration_hash == stable_hash(entry.campaign_config.as_dict())
        assert entry.campaign_config.seeds == (0, 1, 2, 3, 4)
        assert set(entry.output_layout["folders"]) == set(PRODUCTION_OUTPUT_FOLDERS)
        assert entry.provenance["scientific_evidence"] is False
        assert entry.as_dict()["scientific_scope"] == SCIENTIFIC_CAMPAIGN_SCOPE
    benchmark = load_campaign_library_entry(REPO_ROOT / "configs" / "v2" / "campaigns" / "benchmark_suite.json")
    assert benchmark.metadata["planned_experiment_count"] == 1600


def test_deferred_execution_status_checkpoint_and_validation(tmp_path):
    entry = load_campaign_library_entry(REPO_ROOT / "configs" / "v2" / "campaigns" / "healthy_baseline.json")
    report = execute_production_campaign(entry, output_root=tmp_path, max_experiments=2)
    assert report["overall_pass"] is True
    assert report["status"]["completed"] == 2
    assert report["status"]["remaining"] == 3
    checkpoint_path = Path(report["status"]["checkpoint_path"])
    checkpoint = recover_checkpoint(checkpoint_path)
    assert checkpoint.completed_ids
    status = campaign_status(5, checkpoint, checkpoint_path)
    assert isinstance(status, CampaignExecutionStatus)
    assert status.remaining == 3
    validation = validate_scientific_campaign_package(tmp_path, campaign_id=entry.campaign_config.campaign_id)
    assert validation["overall_pass"] is True
    assert set(validation["folder_checks"]) == set(PRODUCTION_OUTPUT_FOLDERS)

    plan = create_campaign(CampaignConfig(campaign_id="x", roles=("Healthy",))).experiments[0]
    executor = FlyGymBatchExecutor(repo_root=REPO_ROOT, require_flygym=False)
    result = executor(plan)
    assert result["status"] in {"deferred", "completed", "failed"}
    if not flygym_available():
        assert result["status"] == "deferred"


def test_dataset_analysis_figures_assets_and_validation_package(tmp_path):
    results = _results()
    dataset_package = build_scientific_dataset_package(results, output_root=tmp_path, campaign_id="science")
    assert dataset_package["overall_pass"] is True
    assert set(dataset_package["layout"]) == set(PRODUCTION_OUTPUT_FOLDERS)

    dataset = CampaignDatasetBuilder("science_dataset").build(results)
    analysis = run_scientific_analysis(dataset, output_dir=tmp_path / "science" / "reports")
    assert analysis["overall_pass"] is True
    assert Path(analysis["report"]).exists()
    assert "PCA" in analysis["analysis"]["embeddings"]
    assert "trajectory_similarity" in analysis["analysis"]["similarities"]

    figures = generate_scientific_figures(results, output_dir=tmp_path / "science" / "figures", formats=("png", "svg", "pdf"))
    assert figures["trajectory_png"].endswith(".png")
    assert all(Path(path).exists() and Path(path).stat().st_size > 0 for path in figures.values())

    assets = build_manuscript_assets(
        figure_files={"trajectory": figures["trajectory_png"]},
        table_files={"descriptive": analysis["descriptive_csv"]},
        statistics_files={"analysis": analysis["report"]},
        output_dir=tmp_path / "science" / "paper_assets",
    )
    assert Path(assets["manifest"]).exists()
    assert Path(assets["figure_captions"]).exists()
    assert Path(assets["table_captions"]).exists()


def test_scientific_production_campaign_cli_deferred(tmp_path):
    script = REPO_ROOT / "scripts" / "run_scientific_production_campaign.py"
    campaign = REPO_ROOT / "configs" / "v2" / "campaigns" / "healthy_baseline.json"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--campaign",
            str(campaign),
            "--output-root",
            str(tmp_path),
            "--max-experiments",
            "1",
            "--allow-deferred-without-flygym",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["execution"]["status"]["completed"] == 1
    assert payload["validation"]["overall_pass"] is True
