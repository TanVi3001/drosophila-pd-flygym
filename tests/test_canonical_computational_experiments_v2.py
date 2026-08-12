from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from drosophila_pd.behavior_platform import (  # noqa: E402
    EXPERIMENT_SCOPE,
    EXPERIMENT_TEMPLATE_TYPES,
    ExperimentDefinition,
    build_campaign_dashboard,
    load_campaign_templates,
    load_experiment_definition,
    load_experiment_library,
    render_experiment_report,
    validate_experiment_definition,
    validate_experiment_library,
    verify_generated_artifacts,
)


EXPERIMENT_ROOT = REPO_ROOT / "configs" / "v2" / "experiments"


def test_experiment_library_schema_hashes_and_scope():
    definitions = load_experiment_library(EXPERIMENT_ROOT)
    ids = {definition.experiment_id for definition in definitions}
    assert ids == {
        "healthy_baseline",
        "candidate_phenotype",
        "progression_stage_0",
        "progression_stage_1",
        "progression_stage_2",
        "progression_stage_3",
        "progression_stage_4",
        "computational_intervention_reference",
        "robustness_benchmark",
        "sensitivity_benchmark",
    }
    for definition in definitions:
        assert definition.hash_valid()
        assert definition.as_dict()["scientific_scope"] == EXPERIMENT_SCOPE
        assert definition.metadata["biological_claims"] is False
        assert definition.random_seeds == (0, 1, 2, 3, 4)
        assert validate_experiment_definition(definition)["overall_pass"] is True
    library_report = validate_experiment_library(EXPERIMENT_ROOT)
    assert library_report["overall_pass"] is True
    assert library_report["experiment_count"] == 10


def test_campaign_templates_are_deterministic_and_complete():
    templates = load_campaign_templates(EXPERIMENT_ROOT / "templates")
    assert {template.template_type for template in templates} == set(EXPERIMENT_TEMPLATE_TYPES)
    for template in templates:
        payload = template.as_dict()
        assert payload["deterministic"] is True
        assert payload["required_fields"]
        assert payload["scientific_scope"] == EXPERIMENT_SCOPE


def test_experiment_report_dashboard_and_artifact_verification(tmp_path):
    definition = load_experiment_definition(EXPERIMENT_ROOT / "healthy_baseline.json")
    artifact = tmp_path / "artifact.json"
    artifact.write_text('{"ok": true}', encoding="utf-8")
    files = render_experiment_report(
        definition,
        descriptive_statistics={"speed": {"mean": 1.0, "std": 0.0}},
        generated_artifacts={"artifact": artifact},
        output_dir=tmp_path / "reports",
        formats=("markdown", "html", "json"),
    )
    assert set(files) == {"markdown", "html", "json"}
    assert all(path.exists() and path.stat().st_size > 0 for path in files.values())
    report = json.loads(files["json"].read_text(encoding="utf-8"))
    assert report["integrity_verification"]["overall_pass"] is True
    assert "Healthy baseline" in files["markdown"].read_text(encoding="utf-8")

    dashboard = build_campaign_dashboard(
        completed=["healthy_baseline"],
        pending=["candidate_phenotype"],
        failed=[],
        dataset_checks={"dataset": True},
        artifact_checks={"artifact": True},
        output_path=tmp_path / "dashboard.json",
    )
    assert dashboard["campaign_progress"]["completion_fraction"] == pytest.approx(0.5)
    assert dashboard["overall_pass"] is True
    assert (tmp_path / "dashboard.json").exists()
    assert verify_generated_artifacts({"missing": tmp_path / "missing.json"})["overall_pass"] is False

    with pytest.raises(ValueError, match="unsupported"):
        render_experiment_report(definition, output_dir=tmp_path / "bad", formats=("pdf",))


def test_invalid_definition_paths_are_rejected(tmp_path):
    original = json.loads((EXPERIMENT_ROOT / "healthy_baseline.json").read_text(encoding="utf-8"))
    original["configuration_hash"] = "bad"
    bad_path = tmp_path / "bad.json"
    bad_path.write_text(json.dumps(original), encoding="utf-8")
    with pytest.raises(ValueError, match="configuration_hash"):
        load_experiment_definition(bad_path)
    data = json.loads((EXPERIMENT_ROOT / "healthy_baseline.json").read_text(encoding="utf-8"))
    data["experiment_type"] = "unknown"
    data["configuration_hash"] = "ignored"
    with pytest.raises(ValueError, match="unsupported"):
        ExperimentDefinition.from_dict(data)


def test_experiment_report_cli(tmp_path):
    script = REPO_ROOT / "scripts" / "run_v2_experiment_report.py"
    dashboard = tmp_path / "dashboard.json"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--experiment",
            str(EXPERIMENT_ROOT / "candidate_phenotype.json"),
            "--output-dir",
            str(tmp_path / "reports"),
            "--dashboard",
            str(dashboard),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["overall_pass"] is True
    assert Path(payload["files"]["json"]).exists()
    assert dashboard.exists()
