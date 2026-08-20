"""Calibrate archived candidate metric reports against cited target records.

This command does not run FlyGym. Candidate reports must already exist and
must contain explicit ``parameters`` and ``metrics`` mappings (or the existing
runner's ``derived_locomotion_metrics`` mapping).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from drosophila_pd.parkinson import (  # noqa: E402
    calibrate_candidates,
    load_phenotype_database,
    write_calibration_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--targets", required=True, help="Phenotype database JSON path.")
    parser.add_argument(
        "--candidate",
        action="append",
        required=True,
        metavar="NAME=PATH",
        help="Archived candidate report; may be supplied multiple times.",
    )
    parser.add_argument(
        "--output",
        default="results/calibration/calibration.json",
        help="Calibration report path.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    database = load_phenotype_database(args.targets)
    candidates = []
    for specification in args.candidate:
        name, path = _split_candidate(specification)
        payload = _load_mapping(path)
        parameters = payload.get("parameters")
        if not isinstance(parameters, dict):
            raise ValueError(f"Candidate {name!r} must contain a parameters mapping.")
        metrics = payload.get("metrics")
        if not isinstance(metrics, dict):
            metrics = payload.get("derived_locomotion_metrics")
        if not isinstance(metrics, dict):
            raise ValueError(
                f"Candidate {name!r} must contain metrics or derived_locomotion_metrics."
            )
        candidates.append(({str(key): value for key, value in parameters.items()}, metrics))

    result = calibrate_candidates(
        candidates,
        database.targets,
        provenance={
            "targets": str(Path(args.targets).resolve()),
            "candidate_names": [spec.split("=", 1)[0] for spec in args.candidate],
            "simulation_executed_by_command": False,
        },
    )
    output = write_calibration_report(result, args.output)
    print(f"Calibration status: {result.status}")
    print(f"Numeric targets: {result.numeric_target_count}")
    print(f"Candidates: {result.candidate_count}")
    print(f"Report: {output}")
    return 0 if result.status == "PASS" else 2


def _split_candidate(specification: str) -> tuple[str, Path]:
    if "=" not in specification:
        raise ValueError("--candidate must use NAME=PATH syntax.")
    name, raw_path = specification.split("=", 1)
    if not name.strip() or not raw_path.strip():
        raise ValueError("--candidate requires non-empty NAME and PATH.")
    return name.strip(), Path(raw_path)


def _load_mapping(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Candidate report {path} must contain a JSON object.")
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
