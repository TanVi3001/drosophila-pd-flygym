# Research Priority for Literature-to-Proxy Mapping

This is a curation priority, not a claim about gene importance or disease
severity. No paper should be downloaded or added automatically by this plan.

## Priority order

### Priority 1: complete and audit the existing PINK1 curation

The repository currently contains a PINK1 curation workspace and a mapping
artifact, while the campaign registry and calibration-target template remain
curator-owned templates. Review existing PINK1 records first:

- confirm paper provenance, genotype, age/sex, control, and assay;
- transcribe exact values from tables, figures, supplements, or text;
- record units, sample size, uncertainty, and time window;
- separate adult walking, climbing, flight, larval crawling, and morphology;
- approve or reject each proxy row manually.

The immediate objective is not to increase the paper count; it is to turn
qualitative candidate mappings into auditable records where the source really
contains compatible quantitative data.

### Priority 2: expand genes with directly comparable locomotion assays

After the PINK1 review is complete, curate Parkin, DJ-1, alpha-synuclein, and
LRRK2 using the same forms and the same inclusion rules. The current repository
does not provide a completed, quantitative registry for these groups. That is
a workspace status, not evidence that the literature lacks the phenotype.

Keep gene, genotype, developmental stage, sex, assay, and intervention context
separate. Do not pool them merely because they share a proxy name.

### Priority 3: fill the proxy-specific gaps

The next searches/curation passes should target:

| Gap | Assay information needed |
| --- | --- |
| `motor_vigor` | Adult walking speed, distance, or climbing with units and controls. |
| `coordination` | Inter-leg timing, gait phase, stepping regularity, or bilateral coordination. |
| `noise` | Within-trial or between-trial variance with an explicit estimator. |
| `delay` / `latency` | Defined stimulus-to-initiation or action response latency. |
| `fatigue` | Repeated-trial or time-resolved decline under a fixed protocol. |
| `freezing` | Arrest-event threshold, minimum duration, and event frequency. |
| `asymmetry` | Labelled left/right measurements and side-pairing rules. |
| `postural_instability` | Direct orientation, balance, COM, or posture stability measurement. |

These are search and extraction requirements, not default values or guaranteed
literature findings.

## Paper selection rule

Prioritize papers that report a compatible assay, a defined numeric endpoint,
control data, sample size, uncertainty/statistics, and traceable figure/table
references. A paper that only reports a generic “locomotor defect” can remain a
validation or background candidate but should not become a calibration target.

## Gene and assay tracking

Use `research/campaign/paper_registry.csv` for the paper inventory and
`research/campaign/curation_progress.csv` for progress. Use
`research/disease_layer_mapping/paper_proxy_mapping.csv` only after extracting
the phenotype. Do not use the current coverage ranking as a biological ranking.

## Stop conditions

Pause curation for a proxy when the assay definition is ambiguous, a value is
only estimated from a plot without an approved procedure, units are missing,
or the genotype/control context is unclear. Record `NEEDS_DATA` rather than
filling a plausible value.
