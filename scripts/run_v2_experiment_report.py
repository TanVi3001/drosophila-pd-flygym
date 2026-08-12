"""Render canonical v2 computational experiment reports."""

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
    build_campaign_dashboard,
    load_experiment_definition,
    render_experiment_report,
    validate_experiment_definition,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render a v2 computational experiment report.")
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dashboard", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    definition = load_experiment_definition(args.experiment)
    validation = validate_experiment_definition(definition)
    files = render_experiment_report(
        definition,
        descriptive_statistics={"definition_valid": validation["overall_pass"]},
        output_dir=args.output_dir,
        formats=("markdown", "html", "json"),
    )
    dashboard = None
    if args.dashboard is not None:
        dashboard = build_campaign_dashboard(
            completed=[definition.experiment_id] if validation["overall_pass"] else [],
            pending=[],
            failed=[] if validation["overall_pass"] else [definition.experiment_id],
            dataset_checks={"definition_only": True},
            artifact_checks={key: path.exists() for key, path in files.items()},
            output_path=args.dashboard,
        )
    payload = {
        "overall_pass": validation["overall_pass"] and all(path.exists() for path in files.values()),
        "validation": validation,
        "files": {key: path.as_posix() for key, path in files.items()},
        "dashboard": dashboard,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
