# Scientific Boundary Check

The validation workflow scans Markdown documentation for unqualified language
that could exceed the imported-data and computational scope of this project.

## Review Categories

- `boundary_disclaimer`: language is explicitly limited, for example "not a
  diagnosis" or "does not provide clinical prediction".
- `potential_overclaim`: language is not locally negated and requires a human
  review before publication.

The scanner is a text review aid. It does not decide whether a scientific
statement is valid and it does not rewrite documentation.

## Current Boundary

The platform supports simulation integration, measurement, visualization,
computational analysis, and artifact validation. It does not provide a
diagnosis, clinical prediction, or clinical biomarker claim. Any conclusion
must remain within the scope of imported rollout data and the documented
computational definitions.

Run:

```powershell
python scripts/validate_research_workflow.py --root . --skip-boundary
```

To run the boundary scan, omit `--skip-boundary`. Findings are written to
`scientific_boundary_report.md` and its JSON companion.

