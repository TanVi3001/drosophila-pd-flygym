"""Compute read-only Parkinson analysis metrics for an imported rollout."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from drosophila_pd.analysis import analyze_rollout  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, help="Dataset directory or rollout.json/rollout.npz path")
    parser.add_argument("--output", default="results", help="Analysis output directory (default: results)")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = analyze_rollout(args.dataset, args.output)
    print(f"Analysis completed for {result.metrics['dataset_id']}")
    print(f"Frames: {result.metrics['frame_count']}")
    print(f"Walking speed (mm/s): {result.metrics['walking_speed_mm_s']}")
    print(f"Total distance (mm): {result.metrics['total_distance_mm']}")
    print(f"Metrics: {result.files['metrics_json']}")
    print(f"Summary: {result.files['summary']}")
    print(f"Dashboard: {result.files['dashboard']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
