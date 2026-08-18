"""Run the existing research workflow behind explicit runtime and data gates.

This file is orchestration only. It delegates dataset generation, experiment
analysis, biomarker calculation, validation, release auditing, and paper
packaging to the existing entry points. It never implements scientific logic
and never fabricates a rollout or a derived result.
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Callable, Mapping


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ALLOWED_STATUSES = frozenset({"READY", "WAITING_RUNTIME", "WAITING_DATASET", "SKIPPED", "FAILED", "PASS"})
STAGE_NAMES = (
    "runtime",
    "dataset",
    "experiment",
    "analysis",
    "biomarkers",
    "validation",
    "release",
    "publication",
)

StageCallable = Callable[[Path], Mapping[str, Any]]


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _load_script(path: Path) -> Any:
    module_name = f"_research_pipeline_{path.stem}_{id(path)}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load script module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _json_write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def _real_datasets(root: Path) -> list[Path]:
    datasets_root = root / "datasets"
    if not datasets_root.is_dir():
        return []
    found: set[Path] = set()
    for name in ("rollout.json", "rollout.npz", "rollout_arrays.npz"):
        found.update(path.parent.resolve() for path in datasets_root.rglob(name) if path.is_file())
    return sorted(found)


def _status_payload(status: str, *, details: Mapping[str, Any] | None = None, error: str = "") -> dict[str, Any]:
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Unsupported pipeline status: {status}")
    payload: dict[str, Any] = {"status": status}
    if details:
        payload["details"] = dict(details)
    if error:
        payload["error"] = error
    return payload


def _default_runtime(root: Path) -> Mapping[str, Any]:
    module = _load_script(root / "scripts" / "check_runtime.py")
    return module.check_runtime(root).as_dict()


def _default_dataset_generation(root: Path) -> Mapping[str, Any]:
    module = _load_script(root / "scripts" / "generate_research_dataset.py")
    return module.generate_research_datasets(repository_root=root, run_suite=False)


def _default_experiment_suite(root: Path) -> Mapping[str, Any]:
    source = root / "src"
    if source.is_dir() and str(source) not in sys.path:
        sys.path.insert(0, str(source))
    from drosophila_pd.experiment_manager import run_experiment_suite

    return run_experiment_suite(
        repository_root=root,
        output_root=root / "results" / "experiments",
        config_dir=root / "experiments",
        resume=True,
    )


def _default_biomarkers(root: Path) -> Mapping[str, Any]:
    source = root / "src"
    if source.is_dir() and str(source) not in sys.path:
        sys.path.insert(0, str(source))
    from drosophila_pd.biomarkers import write_biomarker_report

    output_root = root / "results" / "biomarkers"
    completed = []
    failed: dict[str, str] = {}
    for dataset in _real_datasets(root):
        try:
            report = write_biomarker_report(dataset, output_root / dataset.name)
            completed.append({"dataset_id": dataset.name, "output": report.dataset_dir.as_posix()})
        except (OSError, ValueError, TypeError, KeyError) as error:
            failed[dataset.name] = f"{type(error).__name__}: {error}"
    return {"completed": completed, "failed": failed, "count": len(completed)}


def _default_validation(root: Path) -> Mapping[str, Any]:
    module = _load_script(root / "scripts" / "validate_research_workflow.py")
    output = root / "results" / "research_validation"
    datasets = _real_datasets(root)
    reports = []
    for dataset in datasets:
        validation = module.validate_dataset(dataset, output=output / dataset.name)
        integrity = module.verify_artifact_integrity(dataset, output=output / dataset.name)
        reports.append({"dataset_id": dataset.name, "validation": validation, "integrity": integrity})
    return {"datasets": reports, "count": len(reports)}


def _default_release(root: Path) -> Mapping[str, Any]:
    module = _load_script(root / "scripts" / "build_release_audit.py")
    return module.build_release_audit(root)


def _default_publication(root: Path) -> Mapping[str, Any]:
    module = _load_script(root / "scripts" / "build_release_audit.py")
    return module.build_paper_package(root)


def _invoke(stage: str, callback: StageCallable, root: Path) -> dict[str, Any]:
    try:
        value = dict(callback(root))
    except Exception as error:  # orchestration boundary: persist failure, do not crash the report
        return _status_payload("FAILED", error=f"{stage}: {type(error).__name__}: {error}")
    return value


def _stage_statuses_for_gate(status: str) -> dict[str, dict[str, Any]]:
    result = {name: _status_payload("SKIPPED", details={"blocked_by": status}) for name in STAGE_NAMES}
    result["runtime"] = _status_payload(status)
    if status == "WAITING_RUNTIME":
        result["dataset"] = _status_payload("WAITING_RUNTIME", details={"blocked_by": "runtime"})
    return result


def _write_reports(root: Path, payload: Mapping[str, Any]) -> None:
    results = root / "results"
    _json_write(results / "research_status.json", payload)
    statuses = payload["statuses"]
    lines = [
        "# Research Status",
        "",
        f"Generated: `{payload['generated_at']}`",
        "",
        "| Stage | Status |",
        "| --- | --- |",
    ]
    for name in STAGE_NAMES:
        lines.append(f"| `{name}` | `{statuses[name]['status']}` |")
    lines.extend(["", "## Blockers", ""])
    blockers = payload.get("blockers", [])
    lines.extend(f"- {item}" for item in blockers) if blockers else lines.append("- None recorded")
    lines.extend(["", "Scope: computational orchestration over real imported/simulated artifacts only.", ""])
    (results / "research_status.md").write_text("\n".join(lines), encoding="utf-8")

    progress_lines = ["# Research Progress Summary", "", f"Generated: `{payload['generated_at']}`", ""]
    progress_lines.append("Progress percentages are omitted where the repository has no measured basis.")
    progress_lines.append("")
    for name in STAGE_NAMES:
        progress_lines.append(f"- `{name}`: **{statuses[name]['status']}**")
    progress_lines.extend(["", "No scientific conclusion is inferred from an execution status.", ""])
    (results / "progress_summary.md").write_text("\n".join(progress_lines), encoding="utf-8")

    final_lines = [
        "# Final Execution Report",
        "",
        f"Generated: `{payload['generated_at']}`",
        "",
        "## Completed Steps",
        "",
    ]
    completed = payload.get("completed_steps", [])
    final_lines.extend(f"- `{item}`" for item in completed) if completed else final_lines.append("- None")
    final_lines.extend(["", "## Skipped Steps", ""])
    skipped = payload.get("skipped_steps", [])
    final_lines.extend(f"- `{item}`" for item in skipped) if skipped else final_lines.append("- None")
    final_lines.extend(["", "## Blockers", ""])
    final_lines.extend(f"- {item}" for item in blockers) if blockers else final_lines.append("- None")
    final_lines.extend(["", "## Next Action", "", payload.get("next_action", "No next action recorded."), ""])
    (results / "final_execution_report.md").write_text("\n".join(final_lines), encoding="utf-8")


def run_research_pipeline(
    repository_root: str | Path = REPOSITORY_ROOT,
    *,
    runtime_checker: StageCallable | None = None,
    dataset_generator: StageCallable | None = None,
    experiment_runner: StageCallable | None = None,
    biomarker_runner: StageCallable | None = None,
    validation_runner: StageCallable | None = None,
    release_runner: StageCallable | None = None,
    publication_runner: StageCallable | None = None,
) -> dict[str, Any]:
    """Run the existing workflow and persist status even when a gate waits."""

    root = Path(repository_root).expanduser().resolve()
    runtime_checker = runtime_checker or _default_runtime
    dataset_generator = dataset_generator or _default_dataset_generation
    experiment_runner = experiment_runner or _default_experiment_suite
    biomarker_runner = biomarker_runner or _default_biomarkers
    validation_runner = validation_runner or _default_validation
    release_runner = release_runner or _default_release
    publication_runner = publication_runner or _default_publication

    runtime = _invoke("runtime", runtime_checker, root)
    runtime_ready = bool(runtime.get("overall_pass", runtime.get("runtime_ready", False)))
    if not runtime_ready:
        statuses = _stage_statuses_for_gate("WAITING_RUNTIME")
        statuses["runtime"] = _status_payload("WAITING_RUNTIME", details=runtime)
        payload = _finish_payload(root, statuses, ["Runtime is not ready; downstream steps were not started."], "Install the pinned Python 3.12 FlyGym runtime, then rerun this command.")
        _write_reports(root, payload)
        return payload

    generated = _invoke("dataset", dataset_generator, root)
    datasets = _real_datasets(root)
    if not datasets:
        statuses = _stage_statuses_for_gate("WAITING_DATASET")
        statuses["runtime"] = _status_payload("PASS", details=runtime)
        statuses["dataset"] = _status_payload("WAITING_DATASET", details=generated)
        payload = _finish_payload(root, statuses, ["Dataset generation completed without a usable real rollout."], "Provide or successfully generate a validated rollout, then rerun this command.")
        _write_reports(root, payload)
        return payload
    if generated.get("status") == "FAILED" or generated.get("error"):
        statuses = _stage_statuses_for_gate("FAILED")
        statuses["runtime"] = _status_payload("PASS", details=runtime)
        statuses["dataset"] = _status_payload("FAILED", details=generated)
        payload = _finish_payload(root, statuses, ["Dataset generation failed."], "Inspect the dataset-generation error before rerunning.")
        _write_reports(root, payload)
        return payload

    suite = _invoke("experiment", experiment_runner, root)
    experiment_failed = suite.get("status") == "FAILED" or int(suite.get("counts", {}).get("FAILED", 0)) > 0
    if experiment_failed:
        statuses = _stage_statuses_for_gate("FAILED")
        statuses["runtime"] = _status_payload("PASS", details=runtime)
        statuses["dataset"] = _status_payload("PASS", details={"count": len(datasets), "generation": generated})
        statuses["experiment"] = _status_payload("FAILED", details=suite)
        payload = _finish_payload(root, statuses, ["Experiment suite failed."], "Inspect experiment artifacts and rerun after correcting the failed stage.")
        _write_reports(root, payload)
        return payload
    completed_experiments = int(suite.get("counts", {}).get("COMPLETED", 0))
    if "counts" in suite and completed_experiments == 0:
        statuses = _stage_statuses_for_gate("WAITING_DATASET")
        statuses["runtime"] = _status_payload("PASS", details=runtime)
        statuses["dataset"] = _status_payload("PASS", details={"count": len(datasets), "generation": generated})
        statuses["experiment"] = _status_payload("WAITING_DATASET", details=suite)
        payload = _finish_payload(root, statuses, ["No experiment completed over the discovered rollout artifacts."], "Inspect dataset and experiment records, then rerun this command.")
        _write_reports(root, payload)
        return payload

    biomarker = _invoke("biomarkers", biomarker_runner, root)
    validation = _invoke("validation", validation_runner, root)
    release = _invoke("release", release_runner, root)
    publication = _invoke("publication", publication_runner, root)
    biomarker_pass = bool(biomarker.get("count", 0)) and not biomarker.get("failed")
    validation_reports = validation.get("datasets", [])
    validation_pass = bool(validation_reports) and all(
        report.get("validation", {}).get("overall_pass", False)
        and report.get("integrity", {}).get("overall_pass", False)
        for report in validation_reports
    )
    validation_pass = validation_pass or ("datasets" not in validation and bool(validation.get("count", 0)))
    statuses = {
        "runtime": _status_payload("PASS", details=runtime),
        "dataset": _status_payload("PASS", details={"count": len(datasets), "generation": generated}),
        "experiment": _status_payload("PASS", details=suite),
        "analysis": _status_payload("PASS", details={"delegated_to": "experiment_manager"}),
        "biomarkers": _status_payload("PASS" if biomarker_pass else "FAILED", details=biomarker),
        "validation": _status_payload("PASS" if validation_pass else "FAILED", details=validation),
        "release": _status_payload("PASS" if release.get("readiness") in {"READY", "READY_FOR_REVIEW"} else "FAILED", details=release),
        "publication": _status_payload(
            "FAILED" if publication.get("status") == "FAILED" else ("PASS" if publication.get("status") == "READY" else "WAITING_DATASET"),
            details=publication,
        ),
    }
    blockers = []
    if statuses["biomarkers"]["status"] == "FAILED":
        blockers.append("One or more biomarker reports failed.")
    if statuses["release"]["status"] == "FAILED":
        blockers.append("Release audit is not ready.")
    if statuses["publication"]["status"] != "PASS":
        blockers.append("Publication package is not ready.")
    payload = _finish_payload(root, statuses, blockers, "Review the generated status and validation reports before publication.")
    _write_reports(root, payload)
    return payload


def _finish_payload(root: Path, statuses: Mapping[str, Mapping[str, Any]], blockers: list[str], next_action: str) -> dict[str, Any]:
    completed = [name for name in STAGE_NAMES if statuses[name]["status"] in {"PASS", "READY"}]
    skipped = [name for name in STAGE_NAMES if statuses[name]["status"] in {"SKIPPED", "WAITING_RUNTIME", "WAITING_DATASET"}]
    return {
        "schema_version": 1,
        "generated_at": _now(),
        "repository_root": root.as_posix(),
        "statuses": {name: dict(statuses[name]) for name in STAGE_NAMES},
        "completed_steps": completed,
        "skipped_steps": skipped,
        "blockers": blockers,
        "next_action": next_action,
        "scientific_scope": "Execution status only; no biological or clinical conclusion.",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT, help="Repository root")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_research_pipeline(args.root)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
