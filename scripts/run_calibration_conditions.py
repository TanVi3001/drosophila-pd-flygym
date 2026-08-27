"""Run configured DiseaseLayer conditions through the existing CPG runner."""

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

from drosophila_pd.experiments.calibration_runner import (  # noqa: E402
    load_calibration_conditions,
    run_calibration_conditions,
)
from drosophila_pd.experiments.healthy_baseline import (  # noqa: E402
    load_healthy_baseline_config,
)
from build_viewer_bundle import ViewerBundleError, build_bundle  # noqa: E402


def _repo_path(path: str | Path) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_absolute():
        return candidate
    return (REPO_ROOT / candidate).resolve()


def _export_viewer_artifacts(summary: dict, *, web_root: Path) -> list[dict[str, str]]:
    """Export viewer pose and static bundle for each completed rollout."""

    entries = [summary.get("baseline", {}), *summary.get("conditions", [])]
    exports: list[dict[str, str]] = []
    for entry in entries:
        report_path = _repo_path(entry["report"])
        report = json.loads(report_path.read_text(encoding="utf-8"))
        artifacts = report.get("rollout_artifacts", {})
        output_dir = artifacts.get("output_dir")
        if not isinstance(output_dir, str):
            raise RuntimeError(
                f"Rollout artifacts were not exported for {entry.get('condition_id')}."
            )
        dataset_dir = _repo_path(output_dir)
        pose_path = dataset_dir / "viewer_pose.json"
        from drosophila_pd.viewer_export import export_viewer_pose  # noqa: PLC0415

        pose_result = export_viewer_pose(dataset_dir, pose_path)
        if not pose_result.validation.overall_pass:
            raise RuntimeError(
                f"Viewer pose validation failed for {entry.get('condition_id')}: "
                f"{pose_result.validation.as_dict()}"
            )
        bundle_path = dataset_dir / "viewer_bundle.zip"
        stage, archive, manifest = build_bundle(
            pose_path,
            output=bundle_path,
            web_root=web_root,
        )
        exports.append(
            {
                "condition_id": str(entry.get("condition_id", "")),
                "rollout_dir": dataset_dir.as_posix(),
                "viewer_pose": pose_path.as_posix(),
                "viewer_bundle": archive.as_posix(),
                "bundle_directory": stage.as_posix(),
                "bundle_file_count": str(len(manifest["files"])),
            }
        )
    return exports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline-config",
        type=Path,
        default=REPO_ROOT / "configs" / "experiments" / "healthy_baseline.yaml",
    )
    parser.add_argument(
        "--conditions",
        type=Path,
        default=REPO_ROOT / "configs" / "parkinson" / "calibration_conditions.yaml",
    )
    parser.add_argument(
        "--targets",
        type=Path,
        help="Optional numeric literature target database for calibration.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "results" / "calibration_conditions",
    )
    parser.add_argument(
        "--export-artifacts",
        action="store_true",
        help="Also export raw rollout JSON/NPZ artifacts for each condition.",
    )
    parser.add_argument(
        "--export-viewer",
        action="store_true",
        help="Export rollout artifacts plus viewer_pose.json and viewer_bundle.zip.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        baseline_config = load_healthy_baseline_config(args.baseline_config)
        conditions = load_calibration_conditions(args.conditions)
        summary = run_calibration_conditions(
            baseline_config=baseline_config,
            conditions=conditions,
            output_dir=args.output,
            repo_root=REPO_ROOT,
            targets_path=args.targets,
            export_artifacts=args.export_artifacts or args.export_viewer,
        )
    except Exception as error:  # noqa: BLE001 - CLI prints actionable failure
        print(f"Calibration execution failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 2

    counts = summary["counts"]
    print(f"Baseline: {'PASS' if summary['baseline']['overall_pass'] else 'FAIL'}")
    print(f"Conditions: {counts['passed']}/{counts['requested']} PASS")
    print(f"Calibration: {summary['calibration']['status']}")
    print(f"Summary: {args.output / 'summary.json'}")
    if args.export_viewer:
        try:
            viewer_exports = _export_viewer_artifacts(
                summary,
                web_root=REPO_ROOT / "web",
            )
        except (OSError, TypeError, ValueError, KeyError, RuntimeError, ViewerBundleError) as error:
            print(f"Viewer export failed: {type(error).__name__}: {error}", file=sys.stderr)
            return 2
        summary["viewer_exports"] = viewer_exports
        summary_path = args.output / "summary.json"
        summary_path.write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        for item in viewer_exports:
            print(f"Viewer pose ({item['condition_id']}): {item['viewer_pose']}")
            print(f"Viewer bundle ({item['condition_id']}): {item['viewer_bundle']}")
    if summary["overall_pass"]:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
