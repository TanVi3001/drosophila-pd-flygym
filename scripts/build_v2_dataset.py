"""Build a v2 production dataset package from completed campaign outputs."""

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

from drosophila_pd.behavior_platform import DatasetFactory, DatasetFactoryConfig, synthetic_demo_dataset, write_dataset_reports  # noqa: E402
from drosophila_pd.behavior_platform.dataset_factory import export_dataset  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a v2 Dataset Factory package.")
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--source-root", action="append", default=[])
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--format", dest="formats", action="append", default=["json", "csv", "npz"])
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--synthetic-demo", action="store_true", help="Build a clearly labeled synthetic demo dataset.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.synthetic_demo:
        dataset = synthetic_demo_dataset(dataset_id=args.dataset_id)
        output = Path(args.output_dir) / args.dataset_id
        files = export_dataset(dataset, output, formats=tuple(args.formats))
        reports = write_dataset_reports(dataset, output_dir=output, split_ratios={"train": 0.7, "validation": 0.15, "test": 0.15})
        payload = {
            "overall_pass": all(path.exists() for path in files.values()) and all(path.exists() for path in reports.values()),
            "synthetic": True,
            "files": {key: path.as_posix() for key, path in files.items()},
            "reports": {key: path.as_posix() for key, path in reports.items()},
        }
    else:
        factory = DatasetFactory(
            DatasetFactoryConfig(
                dataset_id=args.dataset_id,
                source_roots=tuple(args.source_root),
                output_dir=args.output_dir,
                export_formats=tuple(args.formats),
            )
        )
        result = factory.build(force=args.force)
        payload = result.as_dict()
        payload["overall_pass"] = bool(result.validation.get("overall_pass"))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
