# Developer Guide

When modifying the Scene Graph:
- Maintain strict renderer independence. No imports from OpenGL or MuJoCo.
- Use Python `dataclasses` to ensure easy JSON serialization.
- All spatial vectors are standard Python tuples (e.g., `(x, y, z)`).
- Rotations must use quaternions in `(w, x, y, z)` format.
