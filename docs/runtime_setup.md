# Runtime Setup

This repository is a computational research platform. The runtime checker is
read-only: it reports whether the environment is ready and never installs
packages or changes the system.

## Supported Runtime

- Python 3.12.x
- FlyGym 2.1.0
- MuJoCo 3.9.0
- `flygym_demo` available in the same Python environment
- Project dependencies installed from `pyproject.toml`

The simulation-dependent commands are intentionally gated. When one of the
simulation dependencies is unavailable, they must stop with
`WAITING_RUNTIME`; no rollout or scientific artifact is fabricated.

## Install the Package

Create an environment with Python 3.12, activate it, then install the package
and the optional simulation dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test,simulation]"
```

On Ubuntu or another Linux shell:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[test,simulation]'
```

Package availability and platform-specific FlyGym/MuJoCo installation details
should be checked against their upstream documentation. This project does not
silently install or substitute those runtimes.

## Check the Environment

From the repository root, run:

```bash
python scripts/check_runtime.py
```

The report checks Python, FlyGym, MuJoCo, `flygym_demo`, core dependencies,
package import, and the repository scripts. A passing runtime check is a
prerequisite for real simulation execution.

## Windows, Ubuntu, and Colab

On Windows, use a Python 3.12 virtual environment and PowerShell activation as
shown above. On Ubuntu, use the `python3.12` environment and verify that the
MuJoCo runtime libraries are available to the active shell. In Google Colab,
run the notebook installation cell first, install the editable package into
the active kernel environment, and then run the same checker:

```python
!python -m pip install -e ".[test,simulation]"
!python scripts/check_runtime.py
```

The notebook is still subject to the same runtime gate. A Colab kernel that
cannot import FlyGym or MuJoCo must stop and report `WAITING_RUNTIME`.

## Common Problems

- **Python version mismatch:** create the environment with Python 3.12.x; do
  not bypass the version gate with a different interpreter.
- **FlyGym or MuJoCo missing:** install the pinned optional simulation set in
  the active environment, then rerun the checker.
- **`flygym_demo` missing:** verify that the installed FlyGym distribution
  exposes the demo package in the same interpreter used by the command.
- **Import works in a notebook but not in a shell:** install the package into
  the active interpreter with `python -m pip install -e .` and confirm
  `python -c "import drosophila_pd"`.
- **Native-library errors:** check the upstream MuJoCo and FlyGym platform
  requirements. The checker reports the failure but does not alter native
  libraries.

## Readiness Commands

After the checker reports PASS, smoke-test the existing workflow:

```bash
python scripts/run_demo.py
python scripts/run_research_pipeline.py
```

These commands operate on real runtime/data only. If the dataset gate is not
ready, the research pipeline stops with `WAITING_DATASET`.
