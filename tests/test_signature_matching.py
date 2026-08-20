from __future__ import annotations

import csv
import json
from pathlib import Path
import subprocess
import sys

import pytest

from drosophila_pd.signature import (
    DiseaseSignature,
    SignatureEmbedding,
    build_signature,
    build_signature_from_directory,
    cosine_distance,
    dynamic_time_warping_distance,
    euclidean_distance,
    match_signatures,
    normalize_signatures,
    validate_normalization_consistency,
    validate_signature,
    validate_signatures,
    write_signature_reports,
)


def _signature(identifier: str, offset: float = 0.0, *, missing: tuple[str, ...] = ()) -> DiseaseSignature:
    values = {
        "walking_speed": 10.0 + offset,
        "stride_length": 2.0 + offset,
        "step_frequency": 4.0 + offset,
        "pause_fraction": 0.1 + offset,
        "heading_variance": 0.2 + offset,
        "turning_rate": 0.3 + offset,
        "symmetry_index": 0.9 - offset,
        "trajectory_efficiency": 0.8 - offset,
        "orientation_stability": 0.7 - offset,
        "joint_velocity_mean": 1.0 + offset,
        "joint_velocity_std": 0.1 + offset,
        "com_displacement": 5.0 + offset,
        "path_length": 7.0 + offset,
    }
    for name in missing:
        values[name] = "unavailable"
    return DiseaseSignature.from_mapping(values, signature_id=identifier, source=("contract-fixture",))


def test_signature_requires_explicit_metric_values_and_preserves_missing():
    signature = DiseaseSignature.from_mapping({"signature_id": "partial", "walking_speed": 1.0})
    assert signature.walking_speed == 1.0
    assert signature.stride_length == "unavailable"
    report = validate_signature(signature)
    assert report["status"] == "PARTIAL"
    assert "stride_length" in report["missing_metrics"]
    with pytest.raises(ValueError):
        DiseaseSignature.from_mapping({"walking_speed": float("nan")})


def test_builder_reads_summary_documents_without_rollout_frames(tmp_path: Path):
    metrics = {
        "dataset_id": "simulation_contract",
        "scalar_metrics": {
            "walking_speed_mm_s": 10.0,
            "path_length_mm": 7.0,
            "heading_variance_rad2": 0.2,
        },
        "derived_locomotion_metrics": {"mean_planar_speed_mm_s": 10.0},
    }
    biomarkers = {
        "dataset_id": "simulation_contract",
        "biomarkers": {
            "symmetry_score": {"value": 0.9},
            "locomotion_efficiency": {"value": 0.8},
        },
    }
    summary = {"dataset_id": "simulation_contract", "turning_rate": 0.3}
    signature = build_signature(metrics=metrics, biomarkers=biomarkers, rollout_summary=summary)
    assert signature.signature_id == "simulation_contract"
    assert signature.walking_speed == 10.0
    assert signature.symmetry_index == 0.9
    assert signature.trajectory_efficiency == 0.8
    assert signature.turning_rate == 0.3
    assert signature.metadata["source_documents"] == ["metrics", "biomarkers", "rollout_summary"]

    root = tmp_path / "dataset"
    (root / "metrics").mkdir(parents=True)
    (root / "metrics" / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
    (root / "biomarkers").mkdir()
    (root / "biomarkers" / "biomarkers.json").write_text(json.dumps(biomarkers), encoding="utf-8")
    (root / "rollout_summary.json").write_text(json.dumps(summary), encoding="utf-8")
    assert build_signature_from_directory(root).signature_id == "dataset"


def test_normalization_methods_require_reference_and_keep_unavailable():
    signatures = (_signature("a", 0.0), _signature("b", 1.0), _signature("c", 2.0, missing=("path_length",)))
    for method in ("zscore", "minmax", "robust"):
        results = normalize_signatures(signatures, method=method)
        assert all(item.method == method for item in results)
        assert results[-1].signature.path_length == "unavailable"
    baseline = _signature("healthy", 0.0)
    result = normalize_signatures((_signature("candidate", 1.0),), method="healthy_baseline", healthy_baseline=baseline)[0]
    assert result.signature.walking_speed == 1.0
    with pytest.raises(ValueError):
        normalize_signatures(signatures, method="zscore", reference=())


def test_distance_and_embedding_contracts():
    first = _signature("first")
    second = _signature("second", 1.0)
    euclidean = euclidean_distance(first, second)
    assert euclidean.available
    assert euclidean.distance == pytest.approx((13**0.5))
    assert cosine_distance(first, second).available
    assert SignatureEmbedding.from_signature(first).available_fields == first.available_fields
    assert dynamic_time_warping_distance(first, second).status == "UNAVAILABLE"
    assert euclidean_distance(_signature("partial", missing=tuple(first.available_fields)), second).status == "UNAVAILABLE"


def test_matcher_ranks_closest_signature_without_optimizer():
    literature = _signature("literature")
    report = match_signatures(literature, (_signature("far", 3.0), _signature("near", 0.01)))
    assert report.ranking[0].signature_id == "near"
    assert report.ranking[0].rank == 1
    assert 0.0 < report.ranking[0].similarity <= 1.0
    assert "medical interpretation" in report.to_mapping()["scientific_scope"]


def test_validation_detects_duplicate_signature_and_normalization_mismatch():
    duplicate_report = validate_signatures((_signature("same"), _signature("same", 1.0)))
    assert duplicate_report["valid"] is False
    assert any(issue["code"] == "DUPLICATE_SIGNATURE" for issue in duplicate_report["issues"])
    normalized = normalize_signatures((_signature("normalized"), _signature("normalized_2", 1.0)), method="minmax")
    mismatch = validate_normalization_consistency((normalized[0].signature, _signature("raw")))
    assert mismatch["valid"] is False
    invalid = validate_signature({"walking_speed": float("inf")})
    assert invalid["valid"] is False
    assert any(issue["code"] == "NON_FINITE" for issue in invalid["issues"])


def test_reports_write_required_artifacts(tmp_path: Path):
    report = match_signatures(_signature("literature"), (_signature("candidate"),))
    paths = write_signature_reports(report, tmp_path)
    assert {path.name for path in paths.values()} == {
        "signature_report.md",
        "signature_similarity.csv",
        "signature_distance_matrix.csv",
        "ranking.json",
    }
    payload = json.loads(paths["ranking"].read_text(encoding="utf-8"))
    assert payload["ranking"][0]["signature_id"] == "candidate"
    with paths["similarity"].open(newline="", encoding="utf-8") as handle:
        assert len(list(csv.DictReader(handle))) == 1


def test_cli_compares_standalone_signature_files(tmp_path: Path):
    literature = tmp_path / "literature.json"
    simulation = tmp_path / "simulation.json"
    literature.write_text(json.dumps(_signature("literature").to_mapping()), encoding="utf-8")
    simulation.write_text(json.dumps(_signature("simulation").to_mapping()), encoding="utf-8")
    script = Path(__file__).parents[1] / "scripts" / "compare_signatures.py"
    result = subprocess.run(
        [sys.executable, str(script), "--literature", str(literature), "--simulation", str(simulation), "--output", str(tmp_path / "output")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "output" / "ranking.json").is_file()
