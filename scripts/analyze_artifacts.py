"""CLI for the read-only research artifact analyzer."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from drosophila_pd.artifact_analyzer import analyze_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--results", type=Path, default=Path("results"))
    parser.add_argument("--datasets", type=Path, default=Path("datasets"))
    parser.add_argument("--paper", type=Path, default=Path("paper"))
    parser.add_argument("--metrics", type=Path, default=Path("metrics"))
    parser.add_argument("--campaign", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--skip-runtime-check", action="store_true", help="Use only for offline artifact inspection.")
    args = parser.parse_args()
    result = analyze_artifacts(
        repo_root=args.root,
        results_dir=args.results,
        datasets_dir=args.datasets,
        paper_dir=args.paper,
        metrics_dir=args.metrics,
        campaign_path=args.campaign,
        output_dir=args.output,
        check_runtime=not args.skip_runtime_check,
    )
    print(f"Status: {result.summary['status']}")
    print(f"Report: {result.output_dir}")
    return 0 if result.summary["status"] != "FAILED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
