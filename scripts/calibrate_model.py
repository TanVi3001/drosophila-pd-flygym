"""Score archived simulation metrics against a literature CSV.

The command never starts FlyGym. It requires both literature records and
archived metrics and writes an auditable computational calibration report.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from drosophila_pd.calibration import (  # noqa: E402
    CalibrationEngine,
    ObjectiveFunction,
    literature_records_to_targets,
    load_literature_csv,
    load_simulation_metrics,
    write_calibration_reports,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--literature", required=True, type=Path, help="Literature CSV path.")
    parser.add_argument("--metrics", required=True, type=Path, help="Archived metrics JSON path.")
    parser.add_argument("--parameters", type=Path, help="Optional JSON parameter mapping.")
    parser.add_argument("--candidate-id", help="Optional candidate id override for one metrics file.")
    parser.add_argument("--loss", choices=("weighted_mse", "weighted_mae", "huber", "cosine"), default="weighted_mse")
    parser.add_argument("--missing-policy", choices=("ignore", "fail"), default="ignore")
    parser.add_argument("--no-normalize", action="store_true")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "results" / "calibration")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        records = load_literature_csv(args.literature)
        targets = literature_records_to_targets(records)
        candidates = list(load_simulation_metrics(args.metrics))
        if args.parameters is not None:
            parameters = _load_mapping(args.parameters)
            if len(candidates) != 1:
                raise ValueError("--parameters can only override one metrics candidate.")
            candidates[0]["parameters"] = parameters
        if args.candidate_id and len(candidates) == 1:
            candidates[0]["candidate_id"] = args.candidate_id
        engine = CalibrationEngine(
            targets,
            objective=ObjectiveFunction(
                method=args.loss,
                normalize=not args.no_normalize,
                missing_policy=args.missing_policy,
            ),
            provenance={
                "literature_path": str(args.literature.resolve()),
                "metrics_path": str(args.metrics.resolve()),
                "simulation_executed_by_engine": False,
            },
        )
        run = engine.evaluate_candidates(candidates)
        paths = write_calibration_reports(run, args.output)
    except Exception as error:  # noqa: BLE001 - CLI provides actionable failure
        print(f"Calibration failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 2

    print(f"Status: {run.status}")
    print(f"Numeric targets: {run.numeric_target_count}")
    print(f"Candidates: {run.candidate_count}")
    print(f"Report: {paths['report']}")
    return 0 if run.status in {"PASS", "UNAVAILABLE_NUMERIC_TARGET"} else 2


def _load_mapping(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"JSON mapping expected at {path}.")
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
