"""Chay Experimental Campaign v1 ma khong tao du lieu khi gate chua dat."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from drosophila_pd.experiments.experimental_campaign import (  # noqa: E402
    FAILED,
    FAILED_CONFIG,
    PASS,
    WAITING_RUNTIME,
    WAITING_TARGET_DATA,
    run_experimental_campaign,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Chay campaign sweep tren FlyGym that sau khi qua runtime va target gate."
    )
    parser.add_argument(
        "--campaign",
        type=Path,
        default=ROOT / "configs" / "experiments" / "campaign_v1.yaml",
        help="Duong dan campaign YAML.",
    )
    parser.add_argument(
        "--baseline-config",
        type=Path,
        default=ROOT / "configs" / "experiments" / "healthy_baseline.yaml",
        help="Cau hinh healthy baseline hien co.",
    )
    parser.add_argument(
        "--targets",
        type=Path,
        default=ROOT / "configs" / "parkinson" / "phenotype_database.template.json",
        help="Numeric target dataset da duoc phe duyet.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Thu muc artifact; mac dinh doc tu output_directory trong YAML.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Root repository dung de tim runtime va pipeline hien co.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = run_experimental_campaign(
            campaign_config=args.campaign,
            baseline_config=args.baseline_config,
            target_path=args.targets,
            output_dir=args.output,
            repo_root=args.root,
        )
    except Exception as error:  # noqa: BLE001 - CLI prints an auditable failure
        print(f"EXPERIMENTAL_CAMPAIGN: FAILED_CONFIG: {type(error).__name__}: {error}", file=sys.stderr)
        return 2

    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    print(f"Campaign status: {payload.get('status')}")
    if payload.get("status") in {WAITING_RUNTIME, WAITING_TARGET_DATA, PASS}:
        return 0
    if payload.get("status") in {FAILED, FAILED_CONFIG}:
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
