# Maintenance Guide

## Backup

Keep source, configuration, manifests, reports, and provenance under version
control. Keep large rollout/video/array artifacts in the approved data store
with checksums and a documented restore path. Never treat a generated result
directory as the only copy of raw data.

## Release cycle

1. Review open issues and protected paths.
2. Run scripts/bootstrap.py and scripts/check_runtime.py.
3. Run compileall, pytest, and git diff --check.
4. Audit manifests, documentation links, citation/version metadata, and release
   notes.
5. Tag only after the release checklist is complete.

## Dependency updates

Change dependencies only in pyproject.toml (and the documented Colab/docs
requirements where a separate environment is intentional). Re-run editable
installation and the full test suite. For FlyGym/MuJoCo, verify the pinned
Python and native runtime rather than assuming a package install is enough.

## CI maintenance

Keep CI on the supported Python version, install dependencies from the project
metadata, and make optional runtime tests skip with a visible reason when the
native runtime is unavailable. Do not hide failures by disabling validation.

## Regression workflow

For every change, identify affected layers, run focused tests first, then the
full suite. Inspect git diff --check and git status. Generated files must be
deterministic and traceable; a failed or interrupted run must not silently
replace an existing artifact.
