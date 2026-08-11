"""Metrics for Drosophila PD FlyGym simulations."""

from .locomotion import check_locomotion_pass_criteria, compute_locomotion_metrics

__all__ = [
    "check_locomotion_pass_criteria",
    "compute_locomotion_metrics",
]
