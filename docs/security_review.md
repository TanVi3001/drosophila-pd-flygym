# Security and Privacy Review

This is a repository-level review of operational risks. It is not a security
certification.

## Secrets

- No credentials, API keys, or tokens belong in source, notebooks, manifests,
  or generated reports.
- Review .env handling and CI secrets before publishing logs or artifacts.
- Redact local paths and private dataset metadata from issue reports.

## Generated artifacts and large files

.gitignore excludes local environments, logs, raw arrays, media, archives, and
generated result trees while preserving selected evidence and directory
anchors. Before committing a result, check its size, provenance, license, and
whether it contains subject or institution metadata.

## File handling

Use explicit repository-relative roots, validate paths before writes, parse
JSON/YAML as structured data, and validate archive members before extraction.
Do not extract untrusted archives into the source tree. Keep temporary files in
an isolated temporary directory and clean them after successful use.

## Reproducibility and privacy risks

Native runtime versions, random seeds, operating-system details, floating-point
libraries, and data ordering can affect outputs. Record them in manifests when
available. Do not publish raw data or identifiers without authorization.

## Review status

The repository has a documented license and citation file. A maintainer should
still review every incoming dataset and generated bundle for secrets, private
paths, identifiers, and unexpected large files before release. No new security
mechanism is introduced by this document.
