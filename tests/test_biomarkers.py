"""Regression tests for the imported-artifact biomarker layer."""

from __future__ import annotations

import json
from pathlib import Path

from drosophila_pd.biomarkers import calculate_biomarkers, compare_biomarkers, write_biomarker_report


def _write_dataset(root: Path, name: str, *, include_metrics: bool = True, include_rollout: bool = True, offset: float = 0.0) -> Path:
    dataset = root / name
    dataset.mkdir(parents=True)
    count = 8
    time_s = [float(index) for index in range(count)]
    trajectory = [[offset + float(index), float(index % 3), 1.0] for index in range(count)]
    heading = [0.05 * index for index in range(count)]
    if include_metrics:
        metrics = {
            "dataset_id": name,
            "scalar_metrics": {"symmetry_index": 0.8, "total_distance_mm": 10.0},
            "timeseries": {
                "time_s": time_s,
                "thorax_position": trajectory,
                "heading_angle_rad": heading,
                "trajectory_curvature_rad_per_mm": [0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.1, 0.2],
            },
        }
        metrics_dir = dataset / "metrics"
        metrics_dir.mkdir()
        (metrics_dir / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
    if include_rollout:
        frames = []
        for index in range(count):
            frames.append(
                {
                    "timestamp_s": float(index),
                    "thorax": trajectory[index],
                    "contact": {"LF": int(index in {0, 2, 4, 6}), "RF": int(index in {1, 3, 5, 7})},
                    "pause": index >= 6,
                }
            )
        (dataset / "rollout.json").write_text(json.dumps({"frames": frames}), encoding="utf-8")
    return dataset


def test_biomarkers_calculate_from_existing_metrics_and_rollout(tmp_path: Path) -> None:
    dataset = _write_dataset(tmp_path, "Healthy_001")

    report = calculate_biomarkers(dataset)

    assert report.biomarkers["locomotion_efficiency"].available
    assert report.biomarkers["stride_variability"].available
    assert report.biomarkers["pause_ratio"].value == 0.25
    assert report.biomarkers["symmetry_score"].value == 0.8
    assert report.biomarkers["disease_severity_score"].available
    assert report.biomarkers["disease_severity_score"].unit == "0-1"
    assert "not a Parkinson's disease diagnosis" in report.as_dict()["scientific_scope"]


def test_missing_metric_is_unavailable_without_fabrication(tmp_path: Path) -> None:
    dataset = _write_dataset(tmp_path, "MissingMetric", include_metrics=False)

    report = calculate_biomarkers(dataset)

    assert report.biomarkers["locomotion_efficiency"].available
    assert report.biomarkers["orientation_drift"].value == "unavailable"
    assert report.biomarkers["turning_stability"].value == "unavailable"
    assert report.biomarkers["symmetry_score"].available
    assert "rollout.json" in report.biomarkers["symmetry_score"].source
    assert report.biomarkers["pause_ratio"].available


def test_missing_rollout_uses_metrics_only_and_marks_event_metrics_unavailable(tmp_path: Path) -> None:
    dataset = _write_dataset(tmp_path, "MetricsOnly", include_rollout=False)

    report = write_biomarker_report(dataset, tmp_path / "results")

    assert report.biomarkers["locomotion_efficiency"].available
    assert report.biomarkers["orientation_drift"].available
    assert report.biomarkers["stride_variability"].value == "unavailable"
    assert report.biomarkers["pause_ratio"].value == "unavailable"
    assert (tmp_path / "results" / "biomarkers.json").is_file()
    assert (tmp_path / "results" / "biomarkers.csv").is_file()
    assert (tmp_path / "results" / "biomarkers.md").is_file()
    assert (tmp_path / "results" / "digital_twin_dashboard.html").read_text(encoding="utf-8").find("Biomarker radar") >= 0


def test_comparison_handles_one_and_multiple_datasets(tmp_path: Path) -> None:
    first = _write_dataset(tmp_path, "Healthy_001")
    second = _write_dataset(tmp_path, "Candidate_001", offset=3.0)

    single = compare_biomarkers([first], tmp_path / "single")
    multiple = compare_biomarkers([first, second], tmp_path / "multiple")

    assert single.as_dict()["comparison_type"] == "single_dataset"
    assert multiple.as_dict()["comparison_type"] == "side_by_side"
    assert multiple.as_dict()["datasets"] == ["Healthy_001", "Candidate_001"]
    assert (tmp_path / "multiple" / "comparison.json").is_file()
    assert (tmp_path / "multiple" / "comparison.csv").is_file()
    assert (tmp_path / "multiple" / "comparison.md").is_file()


def test_no_artifacts_is_an_explicit_input_error(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()

    try:
        calculate_biomarkers(empty)
    except FileNotFoundError as exc:
        assert "metrics.json or rollout.json" in str(exc)
    else:
        raise AssertionError("an empty dataset must not produce fabricated biomarkers")
