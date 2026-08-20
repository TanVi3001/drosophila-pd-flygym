# Project Health Report

Generated on 2026-08-19 from the checked-out repository. This is a software
and maintainability snapshot. No simulation was run and no scientific data was
generated for this report.

## Status

| Area | Status | Basis |
| --- | --- | --- |
| Tests | PASS | 437 passed, 13 skipped, 0 failed |
| Coverage | NOT REPORTED | No verified percentage was generated; no estimate is supplied |
| Documentation | PASS WITH NOTES | 603 Markdown files under docs/ and the requested maintainer guides are present |
| Release metadata | PASS | Version, changelog, release notes, checklist, license, citation, and contributing files are present |
| Runtime | WAITING_RUNTIME | Python 3.13.5 is active; the project target is Python 3.12.x and FlyGym/MuJoCo are unavailable |
| Research execution | WAITING_DATASET | No real rollout files are present in datasets/ |

## Inventory

| Item | Count | Definition |
| --- | ---: | --- |
| Python modules under src/ | 256 | All .py files below src/ |
| Top-level scripts | 42 | All .py files directly below scripts/ |
| Python test files | 144 | Files matching tests/**/test_*.py |
| Python files under tests/ | 147 | All .py files under tests/ |
| Markdown files under docs/ | 603 | All .md files under docs/ |
| Configuration files | 29 | Files under configs/ |

## Test evidence

Command:

    pytest -q -rs -p no:cacheprovider

Result: 437 passed, 13 skipped, 0 failed in 217.17 seconds.

The skipped tests are browser E2E tests requiring the explicit E2E flag and
FlyGym/MuJoCo integration tests requiring the native runtime. They are not
counted as passes.

## Runtime evidence

The canonical read-only checks are:

    python scripts/bootstrap.py
    python scripts/check_runtime.py

The current machine has pip and the repository directories, but it is not a
certified research runtime. Use Python 3.12.x and install the pinned
simulation dependencies according to the project metadata before running
simulation or dataset generation. Bootstrap does not install anything.

## Research readiness

The software test suite is green, but research execution is waiting for two
external conditions: a verified Python/FlyGym/MuJoCo environment and approved
real rollout datasets. No biological or clinical conclusion follows from this
snapshot.

The machine-readable version is at reports/project_health.json.
