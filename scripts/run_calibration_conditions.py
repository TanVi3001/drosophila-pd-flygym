"""Run configured DiseaseLayer conditions through the existing CPG runner."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from drosophila_pd.experiments.calibration_runner import (  # noqa: E402
    load_calibration_conditions,
    run_calibration_conditions,
)
from drosophila_pd.experiments.healthy_baseline import (  # noqa: E402
    load_healthy_baseline_config,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline-config",
        type=Path,
        default=REPO_ROOT / "configs" / "experiments" / "healthy_baseline.yaml",
    )
    parser.add_argument(
        "--conditions",
        type=Path,
        default=REPO_ROOT / "configs" / "parkinson" / "calibration_conditions.yaml",
    )
    parser.add_argument(
        "--targets",
        type=Path,
        help="Optional numeric literature target database for calibration.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "results" / "calibration_conditions",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        baseline_config = load_healthy_baseline_config(args.baseline_config)
        conditions = load_calibration_conditions(args.conditions)
        summary = run_calibration_conditions(
            baseline_config=baseline_config,
            conditions=conditions,
            output_dir=args.output,
            repo_root=REPO_ROOT,
            targets_path=args.targets,
        )
    except Exception as error:  # noqa: BLE001 - CLI prints actionable failure
        print(f"Calibration execution failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 2

    counts = summary["counts"]
    print(f"Baseline: {'PASS' if summary['baseline']['overall_pass'] else 'FAIL'}")
    print(f"Conditions: {counts['passed']}/{counts['requested']} PASS")
    print(f"Calibration: {summary['calibration']['status']}")
    print(f"Summary: {args.output / 'summary.json'}")
    if summary["overall_pass"]:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
