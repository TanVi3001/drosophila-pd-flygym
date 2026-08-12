"""Run v2 scientific production campaign orchestration."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from drosophila_pd.behavior_platform import (  # noqa: E402
    execute_production_campaign,
    load_campaign_library_entry,
    validate_scientific_campaign_package,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a v2 scientific production campaign.")
    parser.add_argument("--campaign", type=Path, required=True, help="Campaign library JSON entry.")
    parser.add_argument("--output-root", type=Path, required=True, help="Root output directory.")
    parser.add_argument("--max-experiments", type=int, help="Optional batch limit for resumable execution.")
    parser.add_argument(
        "--allow-deferred-without-flygym",
        action="store_true",
        help="Record deferred campaign status instead of requiring FlyGym execution.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    entry = load_campaign_library_entry(args.campaign)
    report = execute_production_campaign(
        entry,
        output_root=args.output_root,
        max_experiments=args.max_experiments,
    )
    validation = validate_scientific_campaign_package(args.output_root, campaign_id=entry.campaign_config.campaign_id)
    payload = {"execution": report, "validation": validation}
    print(json.dumps(payload, indent=2, sort_keys=True))
    if args.allow_deferred_without_flygym:
        return 0
    return 0 if report["overall_pass"] and validation["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
