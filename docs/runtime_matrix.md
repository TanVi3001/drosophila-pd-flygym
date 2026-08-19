# Runtime Compatibility Matrix

This matrix records the compatibility target and the result of the local
read-only audit. It is an execution prerequisite, not a claim that a package
is installed everywhere.

| Component | Required version | Current audit status | Notes |
| --- | --- | --- | --- |
| Python | 3.12.x | FAIL in current shell | Current interpreter is Python 3.13.5; use the pinned 3.12 environment. |
| FlyGym | 2.1.0 | WAITING_RUNTIME | `flygym` is not importable in the current environment. |
| MuJoCo | 3.9.0 | WAITING_RUNTIME | `mujoco` is not importable in the current environment. |
| `flygym_demo` | Provided by FlyGym 2.1.0 | WAITING_RUNTIME | The canonical demo helper is not importable without FlyGym. |
| NumPy | >=1.26 | PASS | Current audit observed 2.3.3. |
| Matplotlib | >=3.8,<4 | PASS | Current audit observed 3.10.8. |
| PyYAML | >=6.0 | PASS | Current audit observed 6.0.3. |

## Interpretation

The repository's target is Python 3.12 with FlyGym 2.1.0 and MuJoCo 3.9.0.
The local shell used for this audit is not simulation-ready because the pinned
interpreter and simulation packages are unavailable. No package was installed
and no simulation was run.

Recheck with:

```bash
python scripts/check_runtime.py
```

The runtime gate must report PASS before `run_demo.py`, dataset generation, or
the real research workflow is executed. See
[`runtime_setup.md`](runtime_setup.md) for platform-specific setup guidance.
