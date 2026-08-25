from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from drosophila_pd.evidence import (
    EvidenceCriterion,
    EvidenceValidationError,
    MappingEvidence,
    PaperEvidence,
    ScoringConfig,
    load_evidence_inputs,
    run_evidence_engine,
    score_paper,
)


ROOT = Path(__file__).resolve().parents[1]
PINK1 = ROOT / "research/curation_workspace/pink1"


def test_evidence_engine_reads_pink1_curation_and_writes_all_outputs(tmp_path: Path) -> None:
    paths = run_evidence_engine(
        mapping_csv=PINK1 / "disease_layer_mapping.csv",
        paper_information_json=PINK1 / "paper_information.json",
        candidate_review_csv=PINK1 / "candidate_review.csv",
        output_dir=tmp_path / "evidence",
        scoring_config=ROOT / "configs/evidence/default.yaml",
    )

    assert set(paths) == {
        "evidence_scores.csv",
        "evidence_scores.json",
        "coverage_report.csv",
        "parameter_importance.csv",
        "dependency_matrix.csv",
        "disease_layer_matrix.csv",
        "research_gap.md",
        "evidence_summary.md",
    }
    assert all(path.is_file() for path in paths.values())

    report = json.loads(paths["evidence_scores.json"].read_text(encoding="utf-8"))
    assert report["scientific_scope"].startswith("Evidence completeness")
    assert len(report["papers"]) == 18
    assert len(report["evidence_scores"]) == 18
    assert len(report["coverage"]) == 9
    assert all(not item["quantitative_metric"] for item in report["evidence_scores"])

    with paths["coverage_report.csv"].open(newline="", encoding="utf-8") as handle:
        coverage = list(csv.DictReader(handle))
    motor_vigor = next(row for row in coverage if row["proxy"] == "motor_vigor")
    assert int(motor_vigor["paper_count"]) > 0
    assert int(motor_vigor["quantitative_paper_count"]) == 0


def test_custom_weights_change_score_without_changing_evidence_flags() -> None:
    mapping = MappingEvidence(
        paper_id="P-1",
        phenotype="climbing",
        metric="climbing",
        disease_layer_proxy="motor_vigor",
        confidence="HIGH",
        reason="Named assay.",
        recommended_use="Validation",
        calibration_candidate="conditional",
        validation_candidate="true",
        manual_review_required=True,
        notes="",
    )
    paper = PaperEvidence(
        paper_id="P-1",
        paper={"doi": "10.0000/example", "article_url": "https://example.test/paper", "assays": ["climbing"]},
        candidate={"model": "PINK1 mutant", "age_sex_sample": "n=10; 3 days"},
        mappings=(mapping,),
    )
    config = ScoringConfig(
        criteria=(
            EvidenceCriterion("locomotion_assay", 1),
            EvidenceCriterion("quantitative_metric", 9),
        ),
        high_threshold=90,
        medium_threshold=50,
    )

    result = score_paper(paper, config)

    assert result.criteria == {"locomotion_assay": 1.0, "quantitative_metric": 0.0}
    assert result.score == pytest.approx(10.0)
    assert result.quantitative_metric is False


def test_sample_size_does_not_count_as_quantitative_phenotype() -> None:
    mapping = MappingEvidence(
        paper_id="P-2",
        phenotype="climbing",
        metric="climbing",
        disease_layer_proxy="motor_vigor",
        confidence="HIGH",
        reason="Named assay.",
        recommended_use="Validation",
        calibration_candidate="false",
        validation_candidate="true",
        manual_review_required=True,
        notes="",
    )
    paper = PaperEvidence(
        paper_id="P-2",
        paper={"numeric_values": [], "assays": ["climbing"], "sample_size": "n=20"},
        candidate={"age_sex_sample": "20 male flies; five trials"},
        mappings=(mapping,),
    )
    config = ScoringConfig(
        criteria=(EvidenceCriterion("quantitative_metric", 1), EvidenceCriterion("sample_size", 1))
    )

    result = score_paper(paper, config)

    assert result.quantitative_metric is False
    assert result.sample_size_available is True
    assert result.score == pytest.approx(50.0)


def test_input_join_rejects_unknown_mapping_paper(tmp_path: Path) -> None:
    mapping = tmp_path / "mapping.csv"
    mapping.write_text(
        "paper_id,phenotype,metric,disease_layer_proxy,confidence\n"
        "UNKNOWN,climbing,climbing,motor_vigor,HIGH\n",
        encoding="utf-8",
    )
    candidate = tmp_path / "candidate.csv"
    candidate.write_text("paper_id,model\nP-1,PINK1 mutant\n", encoding="utf-8")
    information = tmp_path / "information.json"
    information.write_text(json.dumps({"papers": [{"paper_id": "P-1"}]}), encoding="utf-8")

    with pytest.raises(EvidenceValidationError, match="unknown paper_id"):
        load_evidence_inputs(mapping, information, candidate)
