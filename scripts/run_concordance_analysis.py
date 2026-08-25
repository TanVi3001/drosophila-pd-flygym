"""Chay Concordance Analysis tren literature va simulation artifact da co."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from drosophila_pd.experiments.concordance import (  # noqa: E402
    PASS,
    WAITING_INPUT_DATA,
    WAITING_SIMULATION,
    run_concordance_analysis,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Doi chieu computational literature evidence voi simulation metrics."
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=ROOT / "results" / "evidence",
        help="Thu muc Evidence Engine output.",
    )
    parser.add_argument(
        "--design-dir",
        type=Path,
        default=ROOT / "research" / "disease_layer_design",
        help="Thu muc Disease Layer Design.",
    )
    parser.add_argument(
        "--campaign",
        type=Path,
        default=ROOT / "results" / "experimental_campaign" / "campaign_data.json",
        help="campaign_data.json cua Experimental Campaign.",
    )
    parser.add_argument(
        "--atlas",
        type=Path,
        default=ROOT / "research" / "phenotype_atlas" / "phenotype_database.json",
        help="Phenotype Atlas JSON.",
    )
    parser.add_argument(
        "--targets",
        type=Path,
        default=ROOT / "research" / "campaign" / "calibration_targets.csv",
        help="Calibration targets CSV neu da duoc phe duyet.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results" / "concordance",
        help="Thu muc bao cao Concordance.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = run_concordance_analysis(
            evidence_dir=args.evidence_dir,
            design_dir=args.design_dir,
            campaign_path=args.campaign,
            output_dir=args.output,
            atlas_path=args.atlas,
            targets_path=args.targets,
        )
    except Exception as error:  # noqa: BLE001 - report the failure clearly
        print(
            f"CONCORDANCE: FAILED: {type(error).__name__}: {error}",
            file=sys.stderr,
        )
        return 2
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    print(f"Concordance status: {payload.get('status')}")
    if payload.get("status") in {PASS, WAITING_SIMULATION, WAITING_INPUT_DATA}:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
