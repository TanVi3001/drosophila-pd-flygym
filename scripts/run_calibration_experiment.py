#!/usr/bin/env python
"""Run the evidence-gated Sprint 5 calibration experiment workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from drosophila_pd.experiments.calibration_experiment import (  # noqa: E402
    WAITING_RUNTIME,
    run_calibration_experiment,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline-config",
        type=Path,
        default=ROOT / "configs" / "experiments" / "healthy_baseline.yaml",
    )
    parser.add_argument(
        "--sweep-config",
        type=Path,
        default=ROOT / "configs" / "parkinson" / "calibration_experiment.yaml",
    )
    parser.add_argument(
        "--targets",
        type=Path,
        default=ROOT / "configs" / "parkinson" / "phenotype_database.template.json",
        help="Approved numeric target database; qualitative/template records are not sufficient.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results" / "calibration_experiment",
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_calibration_experiment(
        baseline_config=args.baseline_config,
        sweep_config=args.sweep_config,
        target_path=args.targets,
        output_dir=args.output,
        repo_root=args.root,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    print(f"Status: {payload['status']}")
    if payload["status"] == WAITING_RUNTIME:
        return 0
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
