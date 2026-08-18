"""Small Git helpers used by repository contract tests."""

from __future__ import annotations

from pathlib import Path
import subprocess


def committed_changes_from_parent(root: Path) -> set[str]:
    """Return committed and working-tree paths changed from the parent.

    A one-commit checkout has no parent to compare against.  In that case the
    test still reports working-tree changes rather than treating a Git history
    error as a passing diff result.
    """

    parent = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD^"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    committed: set[str] = set()
    if parent.returncode == 0 and parent.stdout.strip():
        result = subprocess.run(
            ["git", "diff", "--name-only", parent.stdout.strip(), "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            committed.update(result.stdout.splitlines())

    working_tree = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if working_tree.returncode == 0:
        committed.update(working_tree.stdout.splitlines())
    return committed
