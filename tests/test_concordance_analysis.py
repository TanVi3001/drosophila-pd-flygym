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


def _run(tmp_path: Path, campaign: Path) -> dict:
    return run_concordance_analysis(
        evidence_dir=EVIDENCE,
        design_dir=DESIGN,
        campaign_path=campaign,
        output_dir=tmp_path / "concordance",
        atlas_path=ATLAS,
        targets_path=TARGETS,
    )


def test_missing_simulation_writes_waiting_status_without_rows(tmp_path: Path) -> None:
    payload = _run(tmp_path, tmp_path / "missing_campaign_data.json")
    output = tmp_path / "concordance"

    assert payload["status"] == WAITING_SIMULATION
    assert payload["scientific_results_generated"] is False
    assert payload["agreement"] == []
    assert payload["literature"]["paper_count"] == 18
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

    payload = _run(tmp_path, campaign)
    motor = next(row for row in payload["agreement"] if row["proxy"] == "motor_vigor")

    assert payload["status"] == "PASS"
    assert motor["status"] == INSUFFICIENT
    assert motor["quantitative_paper_count"] == 0
    assert not any(row["status"] in {"Strong", "Moderate", "Weak"} for row in payload["agreement"])
    assert payload["scientific_results_generated"] is True
