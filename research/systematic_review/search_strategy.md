# Search Strategy

This document proposes a search plan only. No database has been queried and
no paper has been downloaded or added to the templates.

## Databases to search

| Database | Planned use | Record-keeping requirement |
|---|---|---|
| PubMed | Biomedical and life-science indexing | Save query, date, filters, and export identifier. |
| Europe PMC | Life-science full-text and metadata discovery | Save query, date, filters, and export identifier. |
| Crossref | DOI and bibliographic discovery | Save query, date, filters, and returned metadata. |
| Google Scholar | Broad supplementary discovery | Record exact query, date, and screened result range. |
| Web of Science | Citation-indexed discovery | Save query, date, database version, and export. |
| Scopus | Citation-indexed discovery | Save query, date, database version, and export. |

Access, licensing, and export policies must be handled by the research team.
The repository does not automate access to any of these services.

## Search concepts

Use combinations of one term from each relevant concept group. Preserve the
exact query syntax separately for each database because operators and field
names differ.

### Gene and disease-model terms

```text
Pink1 OR PINK1 OR Parkin OR PARK2 OR DJ-1 OR DJ1 OR PARK7 OR alpha-synuclein OR SNCA OR LRRK2
```

### Organism terms

```text
Drosophila OR Drosophila melanogaster OR fruit fly
```

### Behavior and assay terms

```text
locomotion OR locomotor OR walking OR gait OR climbing OR negative geotaxis OR turning OR pause OR activity
```

### Measurement terms

```text
walking speed OR velocity OR stride OR step frequency OR turning rate OR movement initiation OR contact
```

## Proposed query combinations

The following are starting points for manual adaptation, not executed queries:

```text
(Pink1 OR Parkin OR DJ-1 OR alpha-synuclein OR LRRK2)
AND (Drosophila OR Drosophila melanogaster OR fruit fly)
AND (locomotion OR walking OR climbing OR turning OR gait)
```

```text
(Pink1 OR Parkin OR DJ-1 OR alpha-synuclein OR LRRK2)
AND (Drosophila OR fruit fly)
AND (walking speed OR stride OR pause OR turning OR movement initiation)
```

```text
(Drosophila OR Drosophila melanogaster)
AND (Parkinson OR parkinsonian OR dopaminergic)
AND (locomotion OR climbing OR negative geotaxis OR gait)
```

## Search limits and documentation

Do not apply date, language, or publication-type limits without recording the
scientific and operational rationale. Record all changes to the proposed
strategy, including pilot terms, database-specific syntax, filters, dates,
export files, and the person who ran the search.

## Deduplication

Deduplicate only after preserving the original database records. Prefer stable
identifiers such as DOI or PMID when available, and send ambiguous matches to
manual review. Do not delete a record solely because metadata are incomplete.
