"""Run the configured imported-rollout experiment suite."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from drosophila_pd.experiment_manager import run_experiment_suite  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run multiple configured rollout analyses sequentially.")
    parser.add_argument("--config", action="append", type=Path, default=None, help="Experiment YAML; repeat for a subset.")
    parser.add_argument("--config-dir", type=Path, default=ROOT / "experiments", help="Directory containing experiment YAML files.")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "experiments", help="Suite output directory.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root.")
    parser.add_argument("--no-resume", action="store_true", help="Re-run completed experiment entries.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_experiment_suite(
        args.config,
        repository_root=args.root,
        output_root=args.output,
        config_dir=args.config_dir,
        resume=not args.no_resume,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("counts", {}).get("FAILED", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
