from __future__ import annotations

import ast
from pathlib import Path
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from drosophila_pd.anatomy import audit


def test_expected_block_8_12_constants_match_documented_checkpoint():
    expected = audit.EXPECTED_BLOCK_8_12

    assert expected["python_major_minor"] == "3.12"
    assert expected["flygym_version"] == "2.1.0"
    assert expected["mujoco_version"] == "3.9.0"
    assert expected["body_segment_count"] == 69
    assert expected["anatomical_joint_count"] == 68
    assert expected["jointdof_count"] == 204
    assert expected["axis_order"] == "PITCH_ROLL_YAW"
    assert expected["axis_counts"] == {"pitch": 68, "roll": 68, "yaw": 68}
    assert expected["leg_jointdof_counts"] == {
        "LF": 24,
        "LM": 24,
        "LH": 24,
        "RF": 24,
        "RM": 24,
        "RH": 24,
    }
    assert expected["non_leg_jointdof_count"] == 60
    assert expected["missing_parent_mjcf_body_count"] == 0
    assert expected["missing_child_mjcf_body_count"] == 0


def test_compare_to_expected_passes_for_exact_expected_observations():
    observed = dict(audit.EXPECTED_BLOCK_8_12)
    observed["jointdof_to_mjcfactuator_by_type_lengths"] = {
        actuator_type: 0 for actuator_type in audit.EXPECTED_ACTUATOR_TYPES
    }
    observed["jointdof_to_neutralaction_by_type_lengths"] = {
        actuator_type: 0 for actuator_type in audit.EXPECTED_ACTUATOR_TYPES
    }

    checks = audit.compare_to_expected(observed)

    assert checks
    assert all(check["pass"] for check in checks.values())


def test_compare_to_expected_flags_changed_invariant():
    observed = dict(audit.EXPECTED_BLOCK_8_12)
    observed["jointdof_count"] = 203
    observed["jointdof_to_mjcfactuator_by_type_lengths"] = {
        actuator_type: 0 for actuator_type in audit.EXPECTED_ACTUATOR_TYPES
    }
    observed["jointdof_to_neutralaction_by_type_lengths"] = {
        actuator_type: 0 for actuator_type in audit.EXPECTED_ACTUATOR_TYPES
    }

    checks = audit.compare_to_expected(observed)

    assert not checks["jointdof_count"]["pass"]


def test_pre_materialization_safety_assertion_rejects_initialized_skeleton():
    class FlyLike:
        skeleton = object()

    with pytest.raises(audit.AuditSafetyError):
        audit.assert_pre_materialized(FlyLike(), phase="test")


def test_python_sources_do_not_call_materializing_methods_or_assign_skeleton():
    forbidden_calls = {
        "add_joints",
        "add_actuators",
        "add_joint_sites",
        "add_leg_adhesion",
    }
    violations = []

    for path in sorted((REPO_ROOT / "src").rglob("*.py")) + sorted(
        (REPO_ROOT / "scripts").rglob("*.py")
    ):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in forbidden_calls:
                    violations.append(f"{path}:{node.lineno} calls {node.func.attr}")
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = list(getattr(node, "targets", [])) or [node.target]
                for target in targets:
                    if isinstance(target, ast.Attribute) and target.attr == "skeleton":
                        violations.append(f"{path}:{node.lineno} assigns skeleton")

    assert violations == []
