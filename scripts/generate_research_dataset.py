"""Generate real FlyGym research datasets and run the existing analysis suite.

This script is orchestration only.  It does not fabricate rollout data, alter
FlyGym, or implement a condition-specific scientific model.  All generated
rollouts come from the configured FlyGym simulation and are first written to a
staging directory so a failed simulation cannot leave an apparently valid
dataset behind.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import UTC, datetime
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any, Callable, Mapping, Sequence

import numpy as np
import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))


class DatasetGenerationError(RuntimeError):
    """Raised when a real dataset cannot be generated or validated."""


class SimulationUnavailableError(DatasetGenerationError):
    """Raised when the required FlyGym runtime is not installed."""


DATASET_GROUPS: tuple[tuple[str, str], ...] = (
    ("healthy", "Healthy"),
    ("pd_mild", "PD_Mild"),
    ("pd_moderate", "PD_Moderate"),
    ("pd_severe", "PD_Severe"),
)
REQUIRED_RAW = ("rollout.json", "rollout.npz", "manifest.json", "metadata.json")
REQUIRED_FIGURES = (
    "speed.png",
    "trajectory.png",
    "orientation.png",
    "joint_velocity.png",
    "joint_acceleration.png",
    "contact_ratio.png",
    "comparison.png",
)
REQUIRED_DERIVED = (
    "viewer_pose.json",
    "metrics/metrics.json",
    "metrics/metrics.csv",
    "report/summary.md",
    "report/dashboard.html",
)
SCIENTIFIC_SCOPE = (
    "Real FlyGym simulation outputs and downstream computational summaries only; "
    "dataset labels do not establish biological Parkinson's disease evidence."
)

SimulationRunner = Callable[[Path, Path, int, str, str], None]


@dataclass
class DatasetResult:
    """Status and artifact counts for one requested dataset."""

    dataset_id: str
    group: str
    path: Path
    status: str
    stages: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    error: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "group": self.group,
            "path": self.path.as_posix(),
            "status": self.status,
            "stages": list(self.stages),
            "missing": list(self.missing),
            "error": self.error,
        }


def generate_research_datasets(
    *,
    repository_root: str | Path = REPOSITORY_ROOT,
    dataset_root: str | Path = "datasets",
    output_root: str | Path = "results/research_dataset_generation",
    config_path: str | Path | None = None,
    count: int = 20,
    steps: int = 100,
    resume: bool = True,
    run_suite: bool = True,
    simulation_runner: SimulationRunner | None = None,
) -> dict[str, Any]:
    """Generate missing datasets, validate them, and analyze completed ones.

    ``simulation_runner`` is an internal test seam; production calls use the
    real FlyGym runner.  It is never used to supply scientific data by the
    command-line workflow.
    """

    if count < 1:
        raise ValueError("count must be positive")
    if steps < 0:
        raise ValueError("steps must be non-negative")
    root = Path(repository_root).expanduser().resolve()
    datasets = _resolve_path(root, dataset_root)
    outputs = _resolve_path(root, output_root)
    config = Path(config_path) if config_path is not None else root / "configs" / "v2" / "flygym" / "healthy.yaml"
    config = config.resolve()
    if not config.is_file():
        raise DatasetGenerationError(f"FlyGym configuration not found: {config}")

    total = len(DATASET_GROUPS) * count
    print(f"Research dataset generation: {total} requested datasets", flush=True)
    results: list[DatasetResult] = []
    for index, (group, prefix) in enumerate(DATASET_GROUPS, start=1):
        group_root = datasets / group
        for number in range(1, count + 1):
            dataset_id = f"{prefix}_{number:03d}"
            dataset_path = group_root / dataset_id
            print(f"[{(index - 1) * count + number}/{total}] {dataset_id}", flush=True)
            result = _process_dataset(
                dataset_id,
                group,
                dataset_path,
                config,
                steps=steps,
                resume=resume,
                simulation_runner=simulation_runner,
                group_root=group_root,
            )
            results.append(result)
            display_status = {"COMPLETED": "Completed", "SKIPPED": "Skipped", "FAILED": "Failed"}.get(result.status, result.status)
            print(display_status, flush=True)

    summary = _build_summary(results, requested=total, steps=steps, config=config)
    outputs.mkdir(parents=True, exist_ok=True)
    _write_json(outputs / "generation_summary.json", summary)
    _write_errors(outputs / "errors.json", results)

    completed_paths = [result.path for result in results if result.status in {"COMPLETED", "SKIPPED"}]
    suite_summary: Mapping[str, Any] | None = None
    if run_suite and completed_paths:
        suite_summary = _run_experiment_suite(
            root,
            completed_paths,
            output_root=outputs / "experiment_suite_configs",
        )
        summary["experiment_suite"] = dict(suite_summary)
        _write_json(outputs / "generation_summary.json", summary)
    elif run_suite:
        summary["experiment_suite"] = {
            "status": "NOT_RUN",
            "reason": "No completed datasets are available for analysis.",
        }
        _write_json(outputs / "generation_summary.json", summary)
    return summary


def _process_dataset(
    dataset_id: str,
    group: str,
    dataset_path: Path,
    config: Path,
    *,
    steps: int,
    resume: bool,
    simulation_runner: SimulationRunner | None,
    group_root: Path,
) -> DatasetResult:
    result = DatasetResult(dataset_id, group, dataset_path, "FAILED")
    if resume and _is_complete(dataset_path):
        result.status = "SKIPPED"
        result.stages.append("Resume")
        return result

    try:
        raw_missing = _missing(dataset_path, REQUIRED_RAW)
        raw_present = [name for name in REQUIRED_RAW if (dataset_path / name).is_file()]
        if raw_missing and raw_present:
            raise DatasetGenerationError(
                "Partial raw rollout package; refusing to mix regenerated and existing files: "
                + ", ".join(raw_missing)
            )
        if raw_missing:
            print("Simulation ...", flush=True)
            if simulation_runner is None:
                _require_simulation_runtime()
                runner = _run_real_simulation
            else:
                runner = simulation_runner
            _generate_into_staging(
                runner,
                dataset_path,
                group_root,
                config,
                steps,
                dataset_id,
                group,
            )
            result.stages.append("Simulation")

        _assert_files(dataset_path, REQUIRED_RAW, "rollout export")
        print("Recorder ...", flush=True)
        result.stages.append("Recorder")
        print("Export ...", flush=True)
        result.stages.append("Export")

        viewer_pose = dataset_path / "viewer_pose.json"
        if not viewer_pose.is_file():
            print("Viewer Pose ...", flush=True)
            from drosophila_pd.viewer_export import export_viewer_pose

            export_viewer_pose(dataset_path, viewer_pose)
        result.stages.append("Viewer Pose")

        derived_missing = _missing(dataset_path, REQUIRED_DERIVED + tuple(f"figures/{name}" for name in REQUIRED_FIGURES))
        if derived_missing:
            print("Analysis ...", flush=True)
            from drosophila_pd.analysis import analyze_rollout

            analyze_rollout(dataset_path, dataset_path)
        result.stages.append("Analysis")
        result.missing = _validate_artifacts(dataset_path)
        if result.missing:
            raise DatasetGenerationError("Dataset validation failed: " + ", ".join(result.missing))
        result.status = "COMPLETED"
    except SimulationUnavailableError:
        raise
    except Exception as error:
        result.error = f"{type(error).__name__}: {error}"
        result.missing = _validate_artifacts(dataset_path)
    return result


def _generate_into_staging(
    runner: SimulationRunner,
    dataset_path: Path,
    group_root: Path,
    config: Path,
    steps: int,
    dataset_id: str,
    group: str,
) -> None:
    group_root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{dataset_id}.", dir=group_root))
    try:
        runner(staging, config, steps, dataset_id, group)
        _assert_files(staging, REQUIRED_RAW, "staged rollout export")
        dataset_path.mkdir(parents=True, exist_ok=True)
        for name in REQUIRED_RAW:
            destination = dataset_path / name
            if not destination.exists():
                shutil.copy2(staging / name, destination)
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _run_real_simulation(dataset_dir: Path, config_path: Path, steps: int, dataset_id: str, group: str) -> None:
    from drosophila_pd.flygym_adapter import (
        FlyGymAdapter,
        FlyGymConfig,
        FlyGymRuntime,
        RolloutRecorder,
        export_rollout,
    )

    config = FlyGymConfig.from_yaml(config_path)
    adapter = FlyGymAdapter()
    simulation = None
    try:
        fly = adapter.create_fly(config.fly)
        world = adapter.create_world(config.world)
        adapter.attach_fly(
            world,
            fly,
            position=config.world.spawn_position,
            orientation=config.world.spawn_orientation,
            add_ground_contact_sensors=config.world.add_ground_contact_sensors,
        )
        simulation = adapter.create_simulation(world, config.simulation)
        simulation.reset()
        timestep = float(getattr(simulation, "timestep", config.simulation.timestep or 0.0))
        recorder = RolloutRecorder(
            simulation,
            fly.name,
            fly=fly,
            timestep=timestep,
            simulation_metadata={
                "dataset_id": dataset_id,
                "condition_group": group,
                "timestep_s": timestep,
                "source": "scripts/generate_research_dataset.py",
                "configuration": config.to_mapping(),
                "scientific_scope": SCIENTIFIC_SCOPE,
            },
        )
        rollout = FlyGymRuntime(simulation, recorder=recorder, max_steps=steps).run()
        if rollout is None or rollout.frame_count <= 0:
            raise DatasetGenerationError("Simulation completed without recorded rollout frames.")
        export_rollout(rollout, dataset_dir)
    except DatasetGenerationError:
        raise
    except Exception as error:
        raise DatasetGenerationError(f"FlyGym simulation failed: {error}") from error
    finally:
        close = getattr(simulation, "close", None)
        if callable(close):
            close()


def _run_experiment_suite(root: Path, dataset_paths: Sequence[Path], *, output_root: Path) -> Mapping[str, Any]:
    from drosophila_pd.experiment_manager import run_experiment_suite

    config_dir = output_root
    config_dir.mkdir(parents=True, exist_ok=True)
    configs: list[Path] = []
    for dataset in sorted(dataset_paths):
        group = dataset.parent.name
        config_path = config_dir / f"{dataset.name}.yaml"
        payload = {
            "experiment_id": dataset.name,
            "name": f"{group} {dataset.name}",
            "condition": group,
            "dataset": dataset.as_posix(),
            "description": "Generated from a completed imported FlyGym rollout.",
            "expected_outputs": ["rollout", "metrics", "report", "figures"],
            "metadata": {"data_policy": "imported_rollout_only", "scientific_scope": SCIENTIFIC_SCOPE},
        }
        config_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
        configs.append(config_path)
    return run_experiment_suite(
        configs,
        repository_root=root,
        output_root=root / "results" / "experiments",
        config_dir=config_dir,
        resume=True,
    )


def _build_summary(results: Sequence[DatasetResult], *, requested: int, steps: int, config: Path) -> dict[str, Any]:
    counts = {status: sum(item.status == status for item in results) for status in ("COMPLETED", "SKIPPED", "FAILED")}
    return {
        "generation_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "requested_datasets": requested,
        "simulation_steps": steps,
        "config": config.as_posix(),
        "counts": counts,
        "datasets": [item.as_dict() for item in results],
        "rollout_count": sum(_has_all(item.path, REQUIRED_RAW) for item in results),
        "viewer_pose_count": sum((item.path / "viewer_pose.json").is_file() for item in results),
        "report_count": sum((item.path / "report" / "summary.md").is_file() for item in results),
        "figure_count": sum(sum((item.path / "figures" / name).is_file() for name in REQUIRED_FIGURES) for item in results),
        "scientific_scope": SCIENTIFIC_SCOPE,
    }


def _write_errors(output_root: Path, results: Sequence[DatasetResult]) -> None:
    errors = [item.as_dict() for item in results if item.status == "FAILED"]
    _write_json(output_root / "errors.json", {"count": len(errors), "datasets": errors})


def _require_simulation_runtime() -> None:
    missing = _missing_simulation_modules()
    if missing:
        names = ", ".join(missing)
        raise SimulationUnavailableError(f"FlyGym runtime unavailable: {names}. Dataset generation stopped.")


def _missing_simulation_modules() -> list[str]:
    return [name for name in ("flygym", "mujoco", "flygym_demo") if importlib.util.find_spec(name) is None]


def _is_complete(path: Path) -> bool:
    return not _validate_artifacts(path)


def _validate_artifacts(path: Path) -> list[str]:
    required = REQUIRED_RAW + REQUIRED_DERIVED + tuple(f"figures/{name}" for name in REQUIRED_FIGURES)
    errors = _missing(path, required)
    if errors:
        return errors
    try:
        payloads = {}
        for name in ("rollout.json", "manifest.json", "metadata.json", "viewer_pose.json", "metrics/metrics.json"):
            payload = json.loads((path / name).read_text(encoding="utf-8"))
            if not isinstance(payload, Mapping):
                errors.append(f"{name}: expected JSON object")
            else:
                payloads[name] = payload
        rollout = payloads.get("rollout.json", {})
        rollout_data = rollout.get("rollout", rollout) if isinstance(rollout, Mapping) else {}
        if not isinstance(rollout_data.get("frames"), list) or not rollout_data["frames"]:
            errors.append("rollout.json: no recorded frames")
        viewer = payloads.get("viewer_pose.json", {})
        if not isinstance(viewer.get("frames"), list) or not viewer["frames"]:
            errors.append("viewer_pose.json: no exported frames")
        elif len(viewer["frames"]) != len(rollout_data.get("frames", ())):
            errors.append("viewer_pose.json: frame count does not match rollout.json")
        metrics = payloads.get("metrics/metrics.json", {})
        if not metrics.get("dataset_id"):
            errors.append("metrics/metrics.json: missing dataset_id")
        with np.load(path / "rollout.npz", allow_pickle=False) as archive:
            if not archive.files:
                errors.append("rollout.npz: no arrays")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"artifact parse error: {error}")
    return errors


def _missing(root: Path, paths: Sequence[str]) -> list[str]:
    return [path for path in paths if not (root / path).is_file()]


def _has_all(root: Path, paths: Sequence[str]) -> bool:
    return not _missing(root, paths)


def _assert_files(root: Path, paths: Sequence[str], stage: str) -> None:
    missing = _missing(root, paths)
    if missing:
        raise DatasetGenerationError(f"{stage} did not produce required files: {', '.join(missing)}")


def _resolve_path(root: Path, value: str | Path) -> Path:
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate real FlyGym rollout datasets and analyze completed outputs.")
    parser.add_argument("--dataset-root", type=Path, default=REPOSITORY_ROOT / "datasets")
    parser.add_argument("--output", type=Path, default=REPOSITORY_ROOT / "results" / "research_dataset_generation")
    parser.add_argument("--config", type=Path, default=REPOSITORY_ROOT / "configs" / "v2" / "flygym" / "healthy.yaml")
    parser.add_argument("--count", type=int, default=20, help="Datasets per group (default: 20).")
    parser.add_argument("--steps", type=int, default=100, help="Simulation steps per dataset (default: 100).")
    parser.add_argument("--no-resume", action="store_true", help="Do not skip already complete datasets.")
    parser.add_argument("--no-experiment-suite", action="store_true", help="Skip the post-generation experiment suite.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        summary = generate_research_datasets(
            repository_root=REPOSITORY_ROOT,
            dataset_root=args.dataset_root,
            output_root=args.output,
            config_path=args.config,
            count=args.count,
            steps=args.steps,
            resume=not args.no_resume,
            run_suite=not args.no_experiment_suite,
        )
    except DatasetGenerationError as error:
        print(f"ERROR: {error}", file=sys.stderr, flush=True)
        return 2
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)
    return 0 if summary["counts"]["FAILED"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
