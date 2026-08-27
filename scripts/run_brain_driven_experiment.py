#!/usr/bin/env python
"""Run a paired locomotion report from a caller-supplied bridge scale file.

This compatibility command consumes a ``bridge_scales.json`` produced by the
separate brain-side project and delegates execution to the existing paired
perturbation experiment. It does not read video files or create scientific
data from summaries.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from drosophila_pd.anatomy.audit import write_json_report  # noqa: E402
from drosophila_pd.experiments.healthy_baseline import (  # noqa: E402
    load_healthy_baseline_config,
)
from drosophila_pd.experiments.perturbation_experiment import (  # noqa: E402
    build_perturbation_unavailable_report,
    run_paired_perturbation_experiment,
)
from drosophila_pd.perturbations import BrainDrivenPerturbation  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scales-json",
        type=Path,
        required=True,
        help="Path to a caller-supplied bridge_scales.json.",
    )
    parser.add_argument(
        "--baseline-config",
        type=Path,
        default=REPO_ROOT / "configs" / "experiments" / "healthy_baseline.yaml",
    )
    parser.add_argument("--model-name", default=None)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    perturbation = BrainDrivenPerturbation.from_json(
        args.scales_json,
        name=f"brain_driven_{args.model_name or ''}".strip("_"),
    )
    baseline_config = load_healthy_baseline_config(args.baseline_config)

    print("Brain-driven computational locomotion experiment")
    print(f"Scales JSON: {args.scales_json}")
    print(f"Model: {perturbation.model}")
    print(f"motor_scale: {perturbation.motor_scale}")
    print(f"coupling_scale: {perturbation.coupling_scale}")

    try:
        report = run_paired_perturbation_experiment(
            baseline_config=baseline_config,
            perturbation=perturbation,
            repo_root=REPO_ROOT,
        )
    except Exception as exc:
        report = build_perturbation_unavailable_report(
            exc,
            baseline_config=baseline_config,
            perturbation=perturbation,
            repo_root=REPO_ROOT,
        )
        print(f"LOCAL EXECUTION = NOT VERIFIED: {type(exc).__name__}: {exc}")
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            write_json_report(report, args.output)
        return 2

    for name, check in report["checks"].items():
        print(f"{'PASS' if check['pass'] else 'FAIL'} {name}")
    status = "PASS" if report["overall_pass"] else "FAIL"
    print(f"Overall: {status}")
    print(report["scientific_scope"])
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        write_json_report(report, args.output)
        print(f"Wrote JSON report: {args.output}")
    return 0 if report["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
