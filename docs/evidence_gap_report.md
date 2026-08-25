# Evidence Gap Report

## Scope and provenance

This is a snapshot of the repository's existing Evidence Engine artifact at
`results/evidence/coverage_report.csv`. It is not a new literature search and
does not add papers or numerical targets. Counts below must be regenerated
after approved curation changes.

The current artifact reports no quantitative papers for any configured proxy.
Therefore every row in `research/simulation_targets.csv` is currently
`WAITING_EVIDENCE`.

## Current proxy coverage

| Proxy | Paper count | Quantitative papers | Qualitative papers | Coverage state | Gap |
| --- | ---: | ---: | ---: | --- | --- |
| `motor_vigor` | 15 | 0 | 15 | qualitative-only | Numeric compatible target and unit are missing. |
| `postural_instability` | 6 | 0 | 6 | qualitative-only | Direct quantitative posture/orientation target is missing. |
| `coordination` | 5 | 0 | 5 | qualitative-only | Direct gait/inter-leg coordination target is missing. |
| `noise` | 1 | 0 | 1 | qualitative-only | Variance definition and numeric target are missing. |
| `latency` | 1 | 0 | 1 | qualitative-only | Explicit response-latency endpoint is missing. |
| `freezing` | 1 | 0 | 1 | qualitative-only | Operational arrest threshold and duration target are missing. |
| `delay` | 0 | 0 | 0 | no-literature in current artifact | A measured initiation-delay endpoint is missing. |
| `fatigue` | 0 | 0 | 0 | no-literature in current artifact | A repeated or time-dependent decline endpoint is missing. |
| `asymmetry` | 0 | 0 | 0 | no-literature in current artifact | A labelled left/right endpoint is missing. |

“No-literature in current artifact” means that the supplied Evidence Engine
inputs contain no mapping for that proxy. It does **not** mean that no such
paper exists in the scientific literature.

## Gap categories

### Many mapped papers, no quantitative target

`motor_vigor`, `postural_instability`, and `coordination` have the largest
current mapping counts, but all are qualitative-only in the stored evidence.
They need source-value extraction, units, uncertainty, assay context, and
manual approval before calibration.

### Low coverage

`noise`, `latency`, and `freezing` each have one mapped paper in the current
artifact. These mappings should be treated as leads for review, not as
calibration support.

### No current mapping

`delay`, `fatigue`, and `asymmetry` have no current mapping record. The next
step is targeted literature curation, not assigning a default parameter or
inventing an expected direction.

### Metric compatibility gaps

The repository has computational metrics such as speed, trajectory geometry,
heading/orientation variance, joint velocity, contact measures, and symmetry
measures. A metric is not compatible merely because its name sounds similar:
the assay definition, unit, time window, and population must be reviewed for
each paper.

## Exit criteria for closing a gap

For a proxy to leave `WAITING_EVIDENCE`, the team should have:

1. an approved paper-to-proxy mapping;
2. a directly reported quantitative literature metric and unit;
3. a documented mapping to an existing simulation metric;
4. sample size and uncertainty/statistical context;
5. a preregistered direction or loss treatment, if direction is scientifically
   justified;
6. a separate validation or holdout plan.

Until these conditions are met, no calibration result or biological conclusion
should be generated.
