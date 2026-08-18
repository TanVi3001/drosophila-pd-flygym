"""Check the local environment required by the real FlyGym workflow.

This command is intentionally read-only.  It does not install packages, run a
simulation, create datasets, or write a report.  Use the installation guide to
repair a failed check, then run this command again.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import importlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable, Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))


PASS = "PASS"
FAIL = "FAIL"
WARN = "WARN"


@dataclass(frozen=True)
class RuntimeCheck:
    """One environment check and its repair-oriented message."""

    name: str
    status: str
    required: bool
    required_version: str
    installed_version: str | None
    message: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RuntimeReport:
    """Structured result returned by :func:`check_runtime`."""

    repository_root: str
    python: str
    checks: tuple[RuntimeCheck, ...]
    runtime_ready: bool
    demo_ready: bool
    dataset_generation_ready: bool
    experiment_suite_ready: bool

    @property
    def overall_pass(self) -> bool:
        """Return whether the real FlyGym runtime is ready."""

        return self.runtime_ready

    def as_dict(self) -> dict[str, Any]:
        return {
            "repository_root": self.repository_root,
            "python": self.python,
            "checks": [check.as_dict() for check in self.checks],
            "readiness": {
                "runtime": self.runtime_ready,
                "demo": self.demo_ready,
                "dataset_generation": self.dataset_generation_ready,
                "experiment_suite": self.experiment_suite_ready,
            },
            "overall_pass": self.overall_pass,
        }


@dataclass(frozen=True)
class DependencySpec:
    """A package import and the distribution version expected by the project."""

    label: str
    module: str
    distribution_names: tuple[str, ...]
    required_version: str
    required: bool = True


DEPENDENCIES: tuple[DependencySpec, ...] = (
    DependencySpec("NumPy", "numpy", ("numpy",), ">=1.26"),
    DependencySpec("PyYAML", "yaml", ("PyYAML",), ">=6.0"),
    DependencySpec("Matplotlib", "matplotlib", ("matplotlib",), ">=3.8,<4"),
    DependencySpec("FlyGym", "flygym", ("flygym",), "==2.1.0"),
    DependencySpec("MuJoCo", "mujoco", ("mujoco",), "==3.9.0"),
    DependencySpec(
        "flygym_demo",
        "flygym_demo",
        ("flygym", "flygym-demo"),
        "provided by FlyGym 2.1.0",
    ),
    DependencySpec("pytest", "pytest", ("pytest",), ">=8.0", required=False),
    DependencySpec("jsonschema", "jsonschema", ("jsonschema",), ">=4.0", required=False),
)


REQUIRED_SCRIPT_PATHS = (
    "scripts/run_demo.py",
    "scripts/generate_research_dataset.py",
    "scripts/run_experiment_suite.py",
)


def _module_spec(module_name: str) -> importlib.machinery.ModuleSpec | None:
    """Return a module spec without allowing broken import hooks to abort checks."""

    try:
        return importlib.util.find_spec(module_name)
    except (ImportError, AttributeError, ValueError):
        return None


def _distribution_version(names: Iterable[str]) -> str | None:
    for name in names:
        try:
            return importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            continue
    return None


def _module_version(module: Any, distribution_names: Iterable[str]) -> str | None:
    distribution = _distribution_version(distribution_names)
    if distribution is not None:
        return distribution
    value = getattr(module, "__version__", None)
    return None if value is None else str(value)


def _version_tuple(value: str) -> tuple[int, ...]:
    numbers = re.findall(r"\d+", value)
    return tuple(int(number) for number in numbers[:4]) or (0,)


def _version_satisfies(installed: str, requirement: str) -> bool:
    """Evaluate the small version constraint grammar used in pyproject.toml."""

    current = _version_tuple(installed)
    for clause in requirement.split(","):
        match = re.fullmatch(r"\s*(==|>=|<=|>|<)\s*([0-9][0-9.]*)\s*", clause)
        if match is None:
            raise ValueError(f"Unsupported version constraint: {requirement}")
        operator, expected_text = match.groups()
        expected = _version_tuple(expected_text)
        if operator == "==" and current != expected:
            return False
        if operator == ">=" and current < expected:
            return False
        if operator == "<=" and current > expected:
            return False
        if operator == ">" and current <= expected:
            return False
        if operator == "<" and current >= expected:
            return False
    return True


def _check_python() -> RuntimeCheck:
    installed = ".".join(str(part) for part in sys.version_info[:3])
    if sys.version_info[:2] == (3, 12):
        return RuntimeCheck(
            "Python",
            PASS,
            True,
            "3.12.x (project runtime target)",
            installed,
            "Supported Python runtime target.",
        )
    return RuntimeCheck(
        "Python",
        FAIL,
        True,
        "3.12.x (project runtime target)",
        installed,
        "Use Python 3.12; the real FlyGym workflow is not certified for this interpreter.",
    )


def _check_dependency(spec: DependencySpec) -> RuntimeCheck:
    if _module_spec(spec.module) is None:
        remedy = f"Install with `python -m pip install -e \".[simulation]\"`" if spec.required else "Install the test extra with `python -m pip install -e \".[test]\"`"
        return RuntimeCheck(
            spec.label,
            FAIL if spec.required else WARN,
            spec.required,
            spec.required_version,
            None,
            f"Module `{spec.module}` is missing. {remedy}.",
        )

    try:
        module = importlib.import_module(spec.module)
    except Exception as exc:  # import-time native-library failures are actionable runtime failures
        return RuntimeCheck(
            spec.label,
            FAIL if spec.required else WARN,
            spec.required,
            spec.required_version,
            None,
            f"Module was found but could not be imported: {type(exc).__name__}: {exc}",
        )

    installed = _module_version(module, spec.distribution_names)
    if spec.label == "flygym_demo":
        return RuntimeCheck(
            spec.label,
            PASS,
            spec.required,
            spec.required_version,
            installed,
            "Package is importable; the canonical helper is checked separately.",
        )
    if installed is None:
        return RuntimeCheck(
            spec.label,
            FAIL if spec.required else WARN,
            spec.required,
            spec.required_version,
            None,
            "Package is importable but its distribution version is unavailable.",
        )
    if not _version_satisfies(installed, spec.required_version):
        return RuntimeCheck(
            spec.label,
            FAIL if spec.required else WARN,
            spec.required,
            spec.required_version,
            installed,
            "Installed version does not satisfy the project requirement.",
        )
    return RuntimeCheck(
        spec.label,
        PASS,
        spec.required,
        spec.required_version,
        installed,
        "Installed version satisfies the project requirement.",
    )


def _check_flygym_helper() -> RuntimeCheck:
    try:
        from flygym_demo.complex_terrain import make_locomotion_fly  # noqa: F401
    except Exception as exc:
        return RuntimeCheck(
            "Canonical FlyGym locomotion helper",
            FAIL,
            True,
            "flygym_demo.complex_terrain.make_locomotion_fly",
            None,
            "The project factory cannot import the canonical helper: "
            f"{type(exc).__name__}: {exc}. Reinstall `flygym==2.1.0` in Python 3.12.",
        )
    return RuntimeCheck(
        "Canonical FlyGym locomotion helper",
        PASS,
        True,
        "flygym_demo.complex_terrain.make_locomotion_fly",
        None,
        "Canonical helper is importable.",
    )


def _check_package_import() -> RuntimeCheck:
    try:
        import drosophila_pd  # noqa: F401
    except Exception as exc:
        return RuntimeCheck(
            "drosophila_pd package import",
            FAIL,
            True,
            "editable install or source checkout",
            None,
            f"Package import failed: {type(exc).__name__}: {exc}. Run `python -m pip install -e .`.",
        )
    return RuntimeCheck(
        "drosophila_pd package import",
        PASS,
        True,
        "editable install or source checkout",
        getattr(sys.modules.get("drosophila_pd"), "__version__", None),
        "Project package is importable.",
    )


def _check_file(root: Path, relative_path: str, *, required: bool = True) -> RuntimeCheck:
    path = root / relative_path
    exists = path.is_file()
    return RuntimeCheck(
        f"Repository file: {relative_path}",
        PASS if exists else (FAIL if required else WARN),
        required,
        "present",
        "present" if exists else None,
        "File is present." if exists else "File is missing.",
    )


def check_runtime(repository_root: str | Path = REPOSITORY_ROOT) -> RuntimeReport:
    """Run all read-only environment and repository preflight checks."""

    root = Path(repository_root).expanduser().resolve()
    source_root = root / "src"
    if source_root.is_dir() and str(source_root) not in sys.path:
        sys.path.insert(0, str(source_root))

    checks: list[RuntimeCheck] = [_check_python()]
    checks.extend(_check_dependency(spec) for spec in DEPENDENCIES)
    checks.append(_check_flygym_helper())
    checks.append(_check_package_import())
    checks.append(_check_file(root, "configs/v2/flygym/healthy.yaml"))
    checks.extend(_check_file(root, path) for path in REQUIRED_SCRIPT_PATHS)

    required_failures = {check.name for check in checks if check.required and check.status == FAIL}
    runtime_ready = not required_failures
    package_ready = all(
        check.status == PASS
        for check in checks
        if check.required and check.name.startswith("Repository file:") or check.name == "drosophila_pd package import"
    )
    core_names = {"Python", "NumPy", "PyYAML", "Matplotlib", "drosophila_pd package import"}
    core_ready = all(check.status == PASS for check in checks if check.name in core_names)
    demo_ready = runtime_ready and package_ready and (root / "scripts/run_demo.py").is_file()
    dataset_generation_ready = runtime_ready and package_ready and (root / "scripts/generate_research_dataset.py").is_file()
    experiment_suite_ready = core_ready and package_ready and (root / "scripts/run_experiment_suite.py").is_file()
    return RuntimeReport(
        repository_root=str(root),
        python=".".join(str(part) for part in sys.version_info[:3]),
        checks=tuple(checks),
        runtime_ready=runtime_ready,
        demo_ready=demo_ready,
        dataset_generation_ready=dataset_generation_ready,
        experiment_suite_ready=experiment_suite_ready,
    )


def _print_report(report: RuntimeReport) -> None:
    print("Drosophila PD FlyGym runtime preflight")
    print(f"Repository: {report.repository_root}")
    print(f"Python: {report.python}")
    print("")
    for check in report.checks:
        version = f"; installed={check.installed_version}" if check.installed_version else ""
        print(f"[{check.status}] {check.name} (required: {check.required_version}{version})")
        print(f"       {check.message}")
    print("")
    print("Readiness (preflight only; no simulation was run):")
    print(f"  Real FlyGym runtime: {'READY' if report.runtime_ready else 'NOT READY'}")
    print(f"  scripts/run_demo.py: {'READY' if report.demo_ready else 'NOT READY'}")
    print(
        "  scripts/generate_research_dataset.py: "
        f"{'READY' if report.dataset_generation_ready else 'NOT READY'}"
    )
    print(f"  scripts/run_experiment_suite.py: {'READY' if report.experiment_suite_ready else 'NOT READY'}")
    if not report.runtime_ready:
        print("Repair failed checks using docs/runtime_environment.md, then run this command again.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT, help="Repository root to inspect.")
    parser.add_argument("--json", action="store_true", help="Print the report as JSON instead of text.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = check_runtime(args.root)
    if args.json:
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    else:
        _print_report(report)
    return 0 if report.overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
