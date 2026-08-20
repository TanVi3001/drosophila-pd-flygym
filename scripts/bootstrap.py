"""Read-only repository bootstrap and runtime preflight.

This command does not install packages, run a simulation, create datasets, or
write generated artifacts. It reports what is available and points a new
checkout to the next documented step.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CORE_DIRECTORIES = ("src", "scripts", "tests", "docs", "configs", "web")
WORKSPACE_DIRECTORIES = ("datasets", "results", "reports", "logs")


@dataclass(frozen=True)
class BootstrapCheck:
    """One read-only bootstrap check."""

    name: str
    status: str
    required: bool
    observed: str | None
    detail: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def check_python() -> BootstrapCheck:
    """Check the supported interpreter without importing scientific modules."""

    observed = ".".join(str(part) for part in sys.version_info[:3])
    supported = sys.version_info[:2] == (3, 12)
    return BootstrapCheck(
        name="Python",
        status="PASS" if supported else "FAIL",
        required=True,
        observed=observed,
        detail="Python 3.12.x is the certified runtime target."
        if supported
        else "Use Python 3.12.x before running the real FlyGym workflow.",
    )


def check_pip() -> BootstrapCheck:
    """Check that pip is available through the active interpreter."""

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return BootstrapCheck(
            name="pip",
            status="FAIL",
            required=True,
            observed=None,
            detail=f"Could not execute pip: {type(exc).__name__}: {exc}",
        )

    output = (result.stdout or result.stderr).strip()
    return BootstrapCheck(
        name="pip",
        status="PASS" if result.returncode == 0 else "FAIL",
        required=True,
        observed=output or None,
        detail="pip is available for the active interpreter."
        if result.returncode == 0
        else "Install or repair pip for the active Python interpreter.",
    )


def check_directories(repository_root: str | Path = REPOSITORY_ROOT) -> list[BootstrapCheck]:
    """Check source directories and report optional output roots separately."""

    root = Path(repository_root).expanduser().resolve()
    checks: list[BootstrapCheck] = []
    for relative in CORE_DIRECTORIES:
        path = root / relative
        exists = path.is_dir()
        checks.append(
            BootstrapCheck(
                name=f"Directory: {relative}",
                status="PASS" if exists else "FAIL",
                required=True,
                observed=str(path) if exists else None,
                detail="Required repository directory is present."
                if exists
                else "Restore the repository directory before running the workflow.",
            )
        )
    for relative in WORKSPACE_DIRECTORIES:
        path = root / relative
        exists = path.is_dir()
        checks.append(
            BootstrapCheck(
                name=f"Workspace directory: {relative}",
                status="PASS" if exists else "INFO",
                required=False,
                observed=str(path) if exists else None,
                detail="Workspace directory is present."
                if exists
                else "Created by the relevant workflow when real inputs are available.",
            )
        )
    return checks


def check_runtime(repository_root: str | Path = REPOSITORY_ROOT) -> dict[str, Any]:
    """Delegate runtime details to the canonical read-only runtime checker."""

    root = Path(repository_root).expanduser().resolve()
    checker = root / "scripts" / "check_runtime.py"
    if not checker.is_file():
        return {
            "overall_pass": False,
            "error": f"Missing runtime checker: {checker}",
        }
    try:
        result = subprocess.run(
            [sys.executable, str(checker), "--root", str(root), "--json"],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {
            "overall_pass": False,
            "error": f"Could not execute runtime checker: {type(exc).__name__}: {exc}",
        }
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {
            "overall_pass": False,
            "error": "Runtime checker did not return valid JSON.",
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    report["exit_code"] = result.returncode
    return report


def build_report(repository_root: str | Path = REPOSITORY_ROOT) -> dict[str, Any]:
    """Build a machine-readable bootstrap report without writing it to disk."""

    checks = [check_python(), check_pip(), *check_directories(repository_root)]
    runtime = check_runtime(repository_root)
    required_pass = all(check.status == "PASS" for check in checks if check.required)
    runtime_pass = bool(runtime.get("overall_pass"))
    status = "READY" if required_pass and runtime_pass else "WAITING_RUNTIME"
    return {
        "repository_root": str(Path(repository_root).expanduser().resolve()),
        "status": status,
        "checks": [check.as_dict() for check in checks],
        "runtime": runtime,
        "next_steps": [
            "Use Python 3.12.x.",
            'Install the package and test dependencies with python -m pip install -e ".[test]".',
            'Install the pinned simulation dependencies with python -m pip install -e ".[simulation]".',
            "Run python scripts/check_runtime.py again.",
            "Only after runtime checks pass, run the documented demo and research workflow.",
        ],
        "side_effects": [],
    }


def _print_report(report: dict[str, Any]) -> None:
    print(f"Bootstrap status: {report['status']}")
    print(f"Repository: {report['repository_root']}")
    for check in report["checks"]:
        print(f"[{check['status']}] {check['name']}: {check['detail']}")
    runtime = report["runtime"]
    print(f"Runtime checker: {'PASS' if runtime.get('overall_pass') else 'WAITING_RUNTIME'}")
    for step, next_step in enumerate(report["next_steps"], start=1):
        print(f"{step}. {next_step}")
    print("No packages were installed and no simulation or dataset was run.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument("--json", action="store_true", help="Print JSON instead of the human report.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_report(args.root)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_report(report)
    return 0 if report["status"] == "READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
