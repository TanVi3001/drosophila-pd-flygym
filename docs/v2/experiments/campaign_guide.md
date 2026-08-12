# Campaign Guide

Experiment definitions connect to campaign IDs under `configs/v2/campaigns/`.
The experiment layer does not execute simulations by itself. It provides
validated definitions and reporting around the production campaign layer.

Reusable templates:

- single experiment;
- parameter sweep;
- robustness study;
- progression study;
- intervention study;
- benchmark study.

Templates are deterministic and intended to keep experiment structure explicit.
