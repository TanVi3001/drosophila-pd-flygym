from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from drosophila_pd.experiments.calibration_runner import (  # noqa: E402
    load_calibration_conditions,
    run_calibration_conditions,
)
from drosophila_pd.experiments.healthy_baseline import HealthyBaselineConfig  # noqa: E402


def _runner(config, layer, condition_id):
    vigor = 1.0 if layer is None else layer.motor_vigor
    return {
        "condition_id": condition_id,
        "overall_pass": True,
        "derived_locomotion_metrics": {
            "mean_planar_speed_mm_s": vigor * 10.0,
            "observations_are_finite": True,
            "derived_metrics_are_finite": True,
        },
    }


def test_condition_config_is_validated_and_deterministic():
    conditions = load_calibration_conditions(
        REPO_ROOT / "configs" / "parkinson" / "calibration_conditions.yaml"
    )

    assert [condition.condition_id for condition in conditions] == [
        "condition_a_vigor_090",
        "condition_a_vigor_080",
        "condition_b_coordination_075",
        "condition_c_delay_010",
    ]
    assert conditions[1].layer.motor_vigor == 0.8
    assert conditions[2].layer.coordination == 0.75


def test_runner_delegates_conditions_and_writes_calibration(tmp_path):
    config = HealthyBaselineConfig.from_mapping({})
    conditions = load_calibration_conditions(
        REPO_ROOT / "configs" / "parkinson" / "calibration_conditions.yaml"
    )[:2]
    summary = run_calibration_conditions(
        baseline_config=config,
        conditions=conditions,
        output_dir=tmp_path,
        repo_root=REPO_ROOT,
        targets_path=None,
        condition_runner=_runner,
    )

    assert summary["overall_pass"] is True
    assert summary["counts"] == {"requested": 2, "passed": 2, "failed": 0}
    assert summary["calibration"]["status"] == "NOT_REQUESTED"
    assert (tmp_path / "healthy_baseline.json").is_file()
    assert (tmp_path / "condition_a_vigor_080.json").is_file()
    assert (tmp_path / "summary.json").is_file()


def test_runner_calibrates_only_completed_conditions(tmp_path):
    config = HealthyBaselineConfig.from_mapping({})
    conditions = load_calibration_conditions(
        REPO_ROOT / "configs" / "parkinson" / "calibration_conditions.yaml"
    )[:2]
    target_file = tmp_path / "targets.json"
    target_file.write_text(
        """{
          \"schema_version\": \"1.0\",
          \"metadata\": {\"purpose\": \"unit test\"},
          \"targets\": [{
            \"target_id\": \"unit_speed\",
            \"metric\": \"mean_planar_speed_mm_s\",
            \"source_id\": \"unit-test\",
            \"citation\": \"unit-test fixture\",
            \"model_context\": \"unit-test\",
            \"assay\": \"unit-test\",
            \"direction\": \"target\",
            \"target_value\": 8.0
          }]
        }""",
        encoding="utf-8",
    )

    summary = run_calibration_conditions(
        baseline_config=config,
        conditions=conditions,
        output_dir=tmp_path / "output",
        repo_root=REPO_ROOT,
        targets_path=target_file,
        condition_runner=_runner,
    )

    assert summary["calibration"]["status"] == "PASS"
    assert summary["calibration"]["best_candidate"]["parameters"]["motor_vigor"] == 0.8
    assert (tmp_path / "output" / "calibration.json").is_file()


def test_runner_records_failed_condition_without_fabricating_report(tmp_path):
    config = HealthyBaselineConfig.from_mapping({})
    conditions = load_calibration_conditions(
        REPO_ROOT / "configs" / "parkinson" / "calibration_conditions.yaml"
    )[:2]

    def failing_runner(config, layer, condition_id):
        if condition_id == "condition_a_vigor_080":
            raise RuntimeError("runtime unavailable in unit test")
        return _runner(config, layer, condition_id)

    summary = run_calibration_conditions(
        baseline_config=config,
        conditions=conditions,
        output_dir=tmp_path,
        repo_root=REPO_ROOT,
        condition_runner=failing_runner,
    )

    assert summary["overall_pass"] is False
    failed = [item for item in summary["conditions"] if item["status"] == "FAILED"]
    assert len(failed) == 1
    assert failed[0]["metrics"] == {}
