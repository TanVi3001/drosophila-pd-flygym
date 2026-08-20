from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from drosophila_pd.calibration import (
    CalibrationEngine,
    LITERATURE_FIELDS,
    ObjectiveFunction,
    ParameterDefinition,
    ParameterSpace,
    compute_loss,
    literature_records_to_targets,
    load_literature_csv,
    load_simulation_metrics,
    validate_calibration_run,
    validate_literature_records,
    write_calibration_reports,
)
from drosophila_pd.calibration.optimizer import GridSearchOptimizer, available_optimizers
from drosophila_pd.calibration.validation import (
    bootstrap_ci,
    leave_one_paper_out,
    mae,
    pearson,
    r_squared,
    rmse,
    spearman,
)


ROOT = Path(__file__).parents[1]


def _write_literature(path: Path, *, include_numeric: bool = True) -> None:
    fields = list(LITERATURE_FIELDS)
    row = {field: "" for field in fields}
    row.update(
        {
            "paper_id": "unit-paper",
            "citation": "Unit test fixture; not scientific evidence.",
            "species": "Drosophila melanogaster",
            "genotype": "unit-control",
            "gene": "none",
            "assay": "unit assay",
            "sex": "mixed",
            "walking_speed_unit": "mm/s",
            "stride_unit": "mm",
            "evidence_level": "unit",
        }
    )
    if include_numeric:
        row["walking_speed"] = "10.0"
        row["stride_length"] = "2.0"
        row["sample_size"] = "4"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow(row)


def test_literature_template_is_empty_and_valid():
    path = ROOT / "research" / "literature" / "phenotype_database.csv"
    records = load_literature_csv(path)
    summary = validate_literature_records(records)
    assert records == ()
    assert summary["valid"] is True
    assert summary["target_count"] == 0


def test_literature_row_preserves_provenance_and_targets(tmp_path):
    path = tmp_path / "literature.csv"
    _write_literature(path)
    records = load_literature_csv(path)
    targets = literature_records_to_targets(records)
    assert len(records) == 1
    assert {target.metric for target in targets} == {"walking_speed", "stride_length"}
    assert targets[0].source_id == "unit-paper"
    assert targets[0].unit in {"mm/s", "mm"}


def test_objectives_support_missing_values_and_all_methods():
    targets = literature_records_to_targets(load_literature_csv(_make_literature_file()))
    for method in ("weighted_mse", "weighted_mae", "huber", "cosine"):
        result = compute_loss(
            {"walking_speed": 11.0, "stride_length": 2.0},
            targets,
            method=method,
        )
        assert result.status == "PASS"
        assert result.loss is not None
    partial = ObjectiveFunction(missing_policy="ignore").evaluate(
        {"walking_speed": 11.0}, targets
    )
    assert partial.status == "PARTIAL"
    assert partial.missing_metrics == ("stride_length",)
    failed = ObjectiveFunction(missing_policy="fail").evaluate(
        {"walking_speed": 11.0}, targets
    )
    assert failed.status == "MISSING_METRICS"


def test_parameter_space_bounds_constraints_and_deterministic_sampling():
    space = ParameterSpace(
        [
            ParameterDefinition("vigor", "continuous", bounds=(0.5, 1.0), default=0.8),
            ParameterDefinition("mode", "categorical", values=("a", "b"), default="a"),
        ],
        constraints=(lambda item: item["vigor"] >= 0.5,),
    )
    assert space.defaults() == {"vigor": 0.8, "mode": "a"}
    assert space.validate({"vigor": 0.7, "mode": "b"})["valid"] is True
    assert space.validate({"vigor": 1.5, "mode": "b"})["valid"] is False
    assert space.sample(3, random_seed=4) == space.sample(3, random_seed=4)

    discrete = ParameterSpace(
        [ParameterDefinition("vigor", "discrete", values=(0.8, 1.0))]
    )
    assert len(discrete.grid()) == 2


def test_optimizer_interface_and_availability():
    space = ParameterSpace([ParameterDefinition("vigor", "discrete", values=(0.8, 1.0))])
    result = GridSearchOptimizer().optimize(space, lambda item: abs(item["vigor"] - 0.8))
    assert result.status == "PASS"
    assert result.best_parameters == {"vigor": 0.8}
    assert available_optimizers()["bayesian"] == "interface_only"


def test_engine_ranks_supplied_candidates_without_simulation():
    targets = literature_records_to_targets(load_literature_csv(_make_literature_file()))
    engine = CalibrationEngine(targets, provenance={"source": "unit-test"})
    run = engine.evaluate_candidates(
        [
            {"candidate_id": "near", "parameters": {"vigor": 1.0}, "metrics": {"walking_speed": 10.0, "stride_length": 2.0}},
            {"candidate_id": "far", "parameters": {"vigor": 0.5}, "metrics": {"walking_speed": 5.0, "stride_length": 1.0}},
        ]
    )
    assert run.status == "PASS"
    assert run.best_candidate_id == "near"
    assert run.provenance["simulation_executed_by_engine"] is False
    assert validate_calibration_run(run)["valid"] is True


def test_engine_keeps_unavailable_targets_explicit():
    targets = literature_records_to_targets(load_literature_csv(_make_literature_file(include_numeric=False)))
    run = CalibrationEngine(targets).evaluate_candidates(
        [{"candidate_id": "candidate", "metrics": {"walking_speed": 10.0}}]
    )
    assert run.status == "UNAVAILABLE_NUMERIC_TARGET"
    assert run.best_candidate_id is None


def test_report_writes_required_artifacts(tmp_path):
    targets = literature_records_to_targets(load_literature_csv(_make_literature_file()))
    run = CalibrationEngine(targets).evaluate_candidates(
        [{"candidate_id": "candidate", "parameters": {"vigor": 1.0}, "metrics": {"walking_speed": 10.0, "stride_length": 2.0}}]
    )
    paths = write_calibration_reports(run, tmp_path)
    assert {path.name for path in paths.values()} == {
        "calibration_report.md",
        "calibration_summary.json",
        "parameter_ranking.csv",
        "objective_breakdown.csv",
    }
    assert json.loads(paths["summary"].read_text())["status"] == "PASS"


def test_validation_statistics_and_leave_one_paper_out():
    observed = [1.0, 2.0, 3.0]
    expected = [1.0, 2.0, 4.0]
    assert rmse(observed, expected) is not None
    assert mae(observed, expected) is not None
    assert r_squared(observed, expected) is not None
    assert pearson(observed, expected) is not None
    assert spearman(observed, expected) == pytest.approx(1.0)
    assert bootstrap_ci(observed, repetitions=50)["status"] == "PASS"
    held_out = leave_one_paper_out(
        [{"paper_id": "a"}, {"paper_id": "b"}],
        lambda records: {"training_count": len(records)},
    )
    assert len(held_out) == 2


def test_metrics_loader_accepts_wrapped_report(tmp_path):
    path = tmp_path / "metrics.json"
    path.write_text(
        json.dumps({"condition_id": "unit", "derived_locomotion_metrics": {"speed": 1.0}}),
        encoding="utf-8",
    )
    candidates = load_simulation_metrics(path)
    assert candidates[0]["candidate_id"] == "candidate_001"
    assert candidates[0]["metrics"]["speed"] == 1.0


def _make_literature_file(*, include_numeric: bool = True) -> Path:
    import tempfile

    path = Path(tempfile.mkstemp(suffix=".csv")[1])
    _write_literature(path, include_numeric=include_numeric)
    return path
