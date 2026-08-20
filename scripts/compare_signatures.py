"""Compare a literature signature with one or more simulation signatures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from drosophila_pd.signature import (  # noqa: E402
    load_signature,
    match_signatures,
    write_signature_reports,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--literature", required=True, help="Literature signature JSON or artifact directory")
    parser.add_argument("--simulation", required=True, nargs="+", help="One or more simulation signatures or artifact directories")
    parser.add_argument("--output", default="results/signature_matching", help="Output directory")
    parser.add_argument(
        "--distance",
        default="euclidean",
        choices=("euclidean", "weighted_euclidean", "cosine", "mahalanobis", "dtw", "earth_mover"),
    )
    parser.add_argument(
        "--normalization",
        default="none",
        choices=("none", "zscore", "minmax", "robust", "healthy_baseline"),
    )
    parser.add_argument("--weights", help="JSON object mapping metric names to weights for weighted Euclidean")
    parser.add_argument("--healthy-baseline", help="Signature JSON or directory used by healthy_baseline normalization")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    literature = load_signature(args.literature)
    simulations = tuple(load_signature(path) for path in args.simulation)
    weights = _load_weights(args.weights) if args.weights else None
    baseline = load_signature(args.healthy_baseline) if args.healthy_baseline else None
    report = match_signatures(
        literature,
        simulations,
        distance_method=args.distance,
        normalization_method=args.normalization,
        weights=weights,
        healthy_baseline=baseline,
    )
    paths = write_signature_reports(report, args.output)
    print(f"Compared {len(report.results)} simulation signatures")
    for item in report.ranking:
        print(f"{item.rank}. {item.signature_id}: distance={item.distance.distance} similarity={item.similarity}")
    print(f"Report: {paths['summary']}")
    print(f"Ranking: {paths['ranking']}")
    return 0


def _load_weights(path: str) -> dict[str, float]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Weights JSON must contain an object.")
    return {str(key): float(value) for key, value in payload.items()}


if __name__ == "__main__":
    raise SystemExit(main())
