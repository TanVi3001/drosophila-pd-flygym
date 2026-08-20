# Digital Phenotype Atlas

This directory is an empty, provenance-first knowledge-base template for
literature phenotypes. It contains no paper values and makes no biological
claim.

Curators may add records only from reviewed local CSV, JSON, or YAML sources.
The parser does not crawl the internet and does not extract numbers from
papers automatically.

Each populated phenotype must retain:

- paper, DOI/PMID, citation context, and model/genotype;
- assay, arena, lighting, camera settings, age, temperature, and sex;
- metric value, unit, sample size, uncertainty, and references;
- manual review state and provenance pointers to figure, table, supplement, and page.

The `provenance` field is an explicit object or JSON string with `paper`,
`figure`, `table`, `supplement`, and `page` keys. Missing information remains
missing and is reported by the validator.
