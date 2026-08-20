"""Validate calibration inputs without running optimization or simulation."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Sequence
from collections.abc import Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from drosophila_pd.calibration import (  # noqa: E402
    literature_records_to_targets,
    load_literature_csv,
    load_simulation_metrics,
    validate_literature_records,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--literature", required=True, type=Path)
    parser.add_argument("--metrics", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "results" / "calibration" / "validation.json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        records = load_literature_csv(args.literature)
        candidates = load_simulation_metrics(args.metrics)
        literature = validate_literature_records(records)
        invalid_metrics = []
        metric_count = 0
        for candidate in candidates:
            for metric, value in candidate["metrics"].items():
                if isinstance(value, (bool, Mapping, list, tuple)) or value is None:
                    continue
                try:
                    finite = math.isfinite(float(value))
                except (TypeError, ValueError):
                    finite = False
                if finite:
                    metric_count += 1
                else:
                    invalid_metrics.append(f"{candidate['candidate_id']}:{metric}")
        report = {
            "valid": bool(literature["valid"]) and not invalid_metrics,
            "literature": literature,
            "candidate_count": len(candidates),
            "finite_metric_count": metric_count,
            "invalid_metrics": invalid_metrics,
            "numeric_target_count": len(literature_records_to_targets(records)),
            "simulation_executed": False,
            "scientific_scope": "Input integrity only; no biological interpretation.",
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except Exception as error:  # noqa: BLE001 - CLI provides actionable failure
        print(f"Validation failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 2

    print(f"Validation: {'PASS' if report['valid'] else 'FAILED'}")
    print(f"Numeric targets: {report['numeric_target_count']}")
    print(f"Report: {args.output}")
    return 0 if report["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
