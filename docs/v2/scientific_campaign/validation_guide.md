# Validation Guide

Production validation checks:

- deterministic campaign replay;
- campaign completeness;
- folder completeness;
- dataset completeness;
- artifact integrity;
- manifest hash consistency;
- provenance availability.

`validate_scientific_campaign_package` writes
`metadata/production_validation_report.json`.

Validation confirms software and artifact integrity only. It does not validate
biological interpretation.
