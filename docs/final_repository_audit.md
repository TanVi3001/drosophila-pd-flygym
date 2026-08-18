# Final Repository Audit

## Strengths

- The repository has a standard Python package layout and dependency metadata.
- FlyGym/MuJoCo integration, rollout recording, export, viewer packaging,
  analysis, experiment management, and biomarker reporting have explicit
  module boundaries.
- Frozen computational evidence, a final report package, provenance manifests,
  and publication/archive documentation are present.
- CI covers Python 3.12 compilation and pytest; Markdown validation is separate.
- The scientific scope repeatedly distinguishes computational simulation from
  real-fly evidence and biological validation.
- `CITATION.cff`, MIT LICENSE, README, community files, and GitHub workflows
  are present.

## Weaknesses

- The current checkout contains no real rollout dataset under `datasets/`.
- The local Windows environment is Python 3.13.5 and lacks FlyGym, MuJoCo, and
  `flygym_demo`, so local real-runtime execution is not verified here.
- Browser E2E and native simulation integrations are conditional on explicit
  runtime dependencies and are skipped in the default local suite when absent.
- LICENSE does not contain an explicit SPDX identifier line.
- `CITATION.cff` has no DOI or journal-specific preferred citation; none is
  invented by this audit.

## Risks

- Native MuJoCo/FlyGym and transitive dependency changes can alter execution or
  rendering behavior.
- Timestamp, figure metadata, JSON serialization, and native rendering outputs
  may differ even when semantic metrics agree.
- Large rollout and video artifacts need an external archival/storage policy.
- A computational condition label must not be presented as a biological disease
  class without external validation.

## Technical Debt

- The README is a long historical/project record and would benefit from a
  maintained navigation index as the platform grows.
- Runtime and browser checks are available, but they are not all exercised in a
  default dependency-light checkout.
- Publication assets are documented, but study-specific generation manifests
  still depend on the future approved dataset.
- SPDX and journal-specific citation metadata should be clarified by the
  repository owner without changing the declared MIT license or inventing a DOI.

## Missing Datasets

The current `datasets/` tree contains `datasets/README.md` only. There is no
rollout package from which to generate new Healthy, computational comparison,
viewer-pose, biomarker, or study-specific publication outputs. This audit does
not create one.

## Missing Biological Validation

The repository does not contain controlled experimental fly data or an external
biological validation study. Simulation outputs, analysis metrics, biomarker
composites, concordance labels, and computational reversibility must therefore
remain computational claims.

## Future Work

- Add an approved, licensed, provenance-complete dataset through the existing
  dataset ingestion path.
- Re-run the full workflow in Python 3.12 with FlyGym 2.1.0 and MuJoCo 3.9.0.
- Complete study-specific statistical, sensitivity, and missing-data review.
- Archive final artifacts and checksums in an appropriate repository or archive.
- Add only owner-approved external biological validation and revise claims
  accordingly.
- Clarify SPDX and preferred-citation metadata when authoritative information
  is available.

## Audit Boundary

This report audits repository structure, documentation, packaging, tests,
workflow support, and declared scientific scope. It does not rerun simulation,
modify evidence, validate a disease model, or certify a journal decision.
