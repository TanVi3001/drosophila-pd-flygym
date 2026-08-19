# Experiment Matrix

This is the Sprint 2 execution plan. It defines intended batch size and
duration only; it does not create rollouts or assert a biological phenotype.

| Group | Dataset count | Steps per dataset | Purpose | Status |
| --- | ---: | ---: | --- | --- |
| Healthy | 20 | 100 | Computational baseline | Planned |
| PD Mild | 20 | 100 | Reserved computational comparison condition | Planned |
| PD Moderate | 20 | 100 | Reserved computational comparison condition | Planned |
| PD Severe | 20 | 100 | Reserved computational comparison condition | Planned |

Expected total: 80 requested datasets. A dataset counts as complete only after
the existing artifact and validation gates pass.

## Configuration Boundary

The repository's generator declares the four group names and dataset ID
patterns. The existing `experiments/pd_mild.yaml`,
`experiments/pd_moderate.yaml`, and `experiments/pd_severe.yaml` are
computational-condition planning entries that require an approved imported
rollout. They do not constitute a validated PD model or a condition-specific
scientific implementation. No disease-stage interpretation is implied by the
labels.

## Execution Order

1. Pass the pinned runtime check.
2. Run a real Healthy smoke dataset and validate every artifact.
3. Complete the Healthy batch with resume enabled.
4. Obtain explicit approved configurations and data for the reserved
   computational comparison groups.
5. Run the existing Experiment Manager, biomarker layer, research validation,
   and publication tooling.

The execution gate stops when a prerequisite is waiting or fails. It does not
replace missing data with synthetic data.
