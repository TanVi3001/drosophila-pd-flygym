from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sys

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from drosophila_pd.parkinson import (  # noqa: E402
    DiseaseLayer,
    PhenotypeTarget,
    calibrate_candidates,
    calibrate_grid,
    load_phenotype_database,
    validate_phenotype_document,
)
from drosophila_pd.perturbations import (  # noqa: E402
    ActionPerturbationContext,
    ControllerPerturbationContext,
    perturbation_from_mapping,
    perturbation_metadata_complete,
)
from drosophila_pd.perturbations.validation import (  # noqa: E402
    summarize_controller_transformation,
)


@dataclass
class _Action:
    joint_angles: np.ndarray
    adhesion_onoff: np.ndarray | None


def _target(metric: str, target_value: float) -> PhenotypeTarget:
    return PhenotypeTarget(
        target_id=f"unit_{metric}",
        metric=metric,
        source_id="unit-test-fixture",
        citation="Unit-test calibration fixture; not scientific evidence.",
        model_context="unit-test metric mapping",
        assay="unit-test",
        direction="target",
        target_value=target_value,
    )


def test_disease_layer_is_deterministic_and_preserves_adhesion():
    layer = DiseaseLayer(
        motor_vigor=0.8,
        initiation_delay_steps=1,
        motor_noise_std=0.05,
        fatigue_rate=0.1,
        random_seed=12,
    )
    action = _Action(np.array([1.0, -2.0]), np.array([True, False]))
    context = ActionPerturbationContext(
        condition_id="unit",
        step_index=3,
        time_s=0.5,
        timestep_s=0.1,
        random_seed=4,
        expected_joint_angle_count=2,
    )

    first = layer.apply_to_action(action, context)
    second = layer.apply_to_action(action, context)

    assert np.array_equal(first.joint_angles, second.joint_angles)
    assert np.array_equal(first.adhesion_onoff, action.adhesion_onoff)
    assert np.isfinite(first.joint_angles).all()
    assert layer.metadata()["scientific_scope"].startswith("A deterministic")


def test_disease_layer_delay_and_asymmetry_are_explicit():
    layer = DiseaseLayer(
        initiation_delay_steps=2,
        asymmetry=0.25,
        left_joint_indices=(0,),
        right_joint_indices=(1,),
    )
    action = _Action(np.array([2.0, 2.0]), None)
    delayed = layer.apply_to_action(
        action,
        ActionPerturbationContext("unit", 1, 0.1, 0.1, 0, 2),
    )
    asymmetric = layer.apply_to_action(
        action,
        ActionPerturbationContext("unit", 2, 0.2, 0.1, 0, 2),
    )

    assert np.array_equal(delayed.joint_angles, np.zeros(2))
    assert np.allclose(asymmetric.joint_angles, [2.5, 1.5])


def test_disease_layer_factory_and_metadata_contract():
    perturbation = perturbation_from_mapping(
        {
            "type": "disease_layer",
            "name": "condition_a",
            "parameters": {"motor_vigor": 0.8, "coordination": 0.75},
        }
    )

    assert isinstance(perturbation, DiseaseLayer)
    assert perturbation.motor_vigor == 0.8
    assert perturbation.coordination == 0.75
    assert perturbation_metadata_complete(perturbation.metadata())


def test_disease_layer_applies_cpg_coordination_without_touching_config():
    class _CPG:
        coupling_weights = np.eye(2)

    class _Controller:
        cpg_network = _CPG()

    controller = _Controller()
    layer = DiseaseLayer(coordination=0.5)
    result = layer.apply_to_controller(
        controller,
        ControllerPerturbationContext("unit", 0.1, 0, 2),
    )

    assert result is controller
    assert np.allclose(controller.cpg_network.coupling_weights, np.eye(2) * 0.5)


def test_disease_layer_controller_summary_reports_coordination_scale():
    layer = DiseaseLayer(coordination=0.75)
    before = {"cpg_coupling_weights": np.eye(2)}
    after = {"cpg_coupling_weights": np.eye(2) * 0.75}

    summary = summarize_controller_transformation(
        pre_controller_state=before,
        post_controller_state=after,
        perturbation_metadata=layer.metadata(),
    )

    assert summary["expected_transform"] == "disease_layer_cpg_coupling_scale"
    assert summary["expected_cpg_coupling_scale"] == 0.75
    assert summary["cpg_coupling_transform_check"]["pass"] is True


def test_calibration_grid_selects_lowest_weighted_loss_and_records_holdout():
    targets = (_target("speed", 8.0), _target("pause_ratio", 0.2))
    holdout = (_target("turning", 1.0),)

    def evaluator(parameters):
        vigor = parameters["motor_vigor"]
        return {
            "speed": vigor * 10.0,
            "pause_ratio": 1.0 - vigor,
            "turning": vigor,
        }

    result = calibrate_grid(
        evaluator,
        {"motor_vigor": [0.6, 0.8, 1.0]},
        targets,
        holdout_targets=holdout,
        random_seed=7,
        provenance={"source": "unit-test fixture"},
    )

    assert result.status == "PASS"
    assert result.best_candidate is not None
    assert result.best_candidate.parameters == {"motor_vigor": 0.8}
    assert result.holdout["status"] == "PASS"
    assert result.provenance["random_seed"] == 7


def test_calibration_does_not_invent_numeric_targets():
    qualitative = PhenotypeTarget(
        target_id="qualitative",
        metric="speed",
        source_id="source",
        citation="Qualitative unit-test fixture.",
        model_context="unit-test",
        assay="unit-test",
        direction="lower",
    )

    result = calibrate_grid(
        lambda parameters: {"speed": 1.0},
        {"motor_vigor": [0.8]},
        [qualitative],
    )

    assert result.status == "UNAVAILABLE_NUMERIC_TARGET"
    assert result.candidate_count == 0
    assert result.best_candidate is None


def test_archived_candidate_calibration_keeps_candidate_parameters():
    result = calibrate_candidates(
        [
            ({"motor_vigor": 0.8}, {"speed": 8.0}),
            ({"motor_vigor": 0.6}, {"speed": 6.0}),
        ],
        [_target("speed", 8.0)],
        provenance={"source": "unit-test fixture"},
    )

    assert result.status == "PASS"
    assert result.best_candidate is not None
    assert result.best_candidate.parameters == {"motor_vigor": 0.8}


def test_phenotype_database_template_is_provenance_validated():
    path = REPO_ROOT / "configs" / "parkinson" / "phenotype_database.template.json"
    database = load_phenotype_database(path)
    summary = validate_phenotype_document(json.loads(path.read_text(encoding="utf-8")))

    assert len(database.targets) == 2
    assert len(database.numeric_targets) == 0
    assert summary["valid"] is True
    assert summary["numeric_target_count"] == 0
