"""Regression tests cho Concordance Analysis, khong tao du lieu khoa hoc."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from drosophila_pd.experiments.concordance import (
    INSUFFICIENT,
    WAITING_SIMULATION,
    run_concordance_analysis,
)
from drosophila_pd.experiments.experimental_campaign import KNOWN_PROXIES


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "results" / "evidence"
DESIGN = ROOT / "research" / "disease_layer_design"
ATLAS = ROOT / "research" / "phenotype_atlas" / "phenotype_database.json"
TARGETS = ROOT / "research" / "campaign" / "calibration_targets.csv"


def _run(tmp_path: Path, campaign: Path, *, qualitative_evidence: bool = False) -> dict:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    for filename, header in {
        "coverage_report.csv": "proxy,paper_count,quantitative_paper_count\n",
        "dependency_matrix.csv": "proxy,metric\n",
        "evidence_scores.csv": "paper_id,proxy,evidence_score\n",
        "disease_layer_matrix.csv": "metric,proxy\n",
    }.items():
        (evidence / filename).write_text(header, encoding="utf-8")
    if qualitative_evidence:
        (evidence / "coverage_report.csv").write_text(
            "proxy,paper_count,quantitative_paper_count\n"
            "motor_vigor,1,0\n",
            encoding="utf-8",
        )
        (evidence / "dependency_matrix.csv").write_text(
            "proxy,metric\n"
            "motor_vigor,walking_speed\n",
            encoding="utf-8",
        )
    design = tmp_path / "design"
    design.mkdir()
    (design / "proxy_design.csv").write_text("proxy\n", encoding="utf-8")
    return run_concordance_analysis(
        evidence_dir=evidence,
        design_dir=design,
        campaign_path=campaign,
        output_dir=tmp_path / "concordance",
        atlas_path=tmp_path / "missing_atlas.json",
        targets_path=tmp_path / "missing_targets.csv",
    )


def test_missing_simulation_writes_waiting_status_without_rows(tmp_path: Path) -> None:
    payload = _run(tmp_path, tmp_path / "missing_campaign_data.json")
    output = tmp_path / "concordance"

    assert payload["status"] == WAITING_SIMULATION
    assert payload["scientific_results_generated"] is False
    assert payload["agreement"] == []
    assert payload["literature"]["paper_count"] == 0
    assert payload["literature"]["atlas"]["record_count"] == 0
    assert set(path.name for path in output.iterdir()) == {
        "agreement.csv",
        "agreement.json",
        "agreement.md",
        "proxy_validation.csv",
        "metric_validation.csv",
        "concordance_matrix.csv",
        "research_findings.md",
        "limitations.md",
        "future_proxy.md",
    }

    with (output / "concordance_matrix.csv").open(newline="", encoding="utf-8") as handle:
        header = next(csv.reader(handle))
    assert header == ["metric", *KNOWN_PROXIES]


def test_available_simulation_does_not_upgrade_qualitative_evidence(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign_data.json"
    campaign.write_text(
        json.dumps(
            {
                "status": "PASS",
                "baseline": [
                    {
                        "status": "COMPLETED",
                        "metrics": {
                            "mean_planar_speed_mm_s": 10.0,
                            "trajectory_efficiency": 0.8,
                        },
                    }
                ],
                "conditions": [
                    {
                        "status": "COMPLETED",
                        "proxy": "motor_vigor",
                        "parameter_value": 0.8,
                        "metrics": {
                            "mean_planar_speed_mm_s": 8.0,
                            "trajectory_efficiency": 0.7,
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    payload = _run(tmp_path, campaign, qualitative_evidence=True)
    motor = next(row for row in payload["agreement"] if row["proxy"] == "motor_vigor")

    assert payload["status"] == "PASS"
    assert motor["status"] == INSUFFICIENT
    assert motor["quantitative_paper_count"] == 0
    assert not any(row["status"] in {"Strong", "Moderate", "Weak"} for row in payload["agreement"])
    assert payload["scientific_results_generated"] is True
