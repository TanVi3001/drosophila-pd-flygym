from __future__ import annotations

import json
from pathlib import Path

import pytest

from drosophila_pd.literature import (
    PhenotypeDatabase,
    PhenotypeRecord,
    Provenance,
    build_knowledge_graph,
    build_statistics,
    find_by_assay,
    find_by_gene,
    find_by_metric,
    find_by_quality,
    find_by_year,
    load_database,
    parse_source,
    validate_database,
    write_atlas_report,
)
from drosophila_pd.literature.models import PHENOTYPE_ATLAS_FIELDS


ROOT = Path(__file__).parents[1]
ATLAS = ROOT / "research" / "phenotype_atlas"


def _contract_record(**overrides):
    values = {field: None for field in PHENOTYPE_ATLAS_FIELDS}
    values.update(
        {
            "paper_id": "contract-fixture",
            "title": "Contract fixture, not a scientific observation",
            "species": "Drosophila melanogaster",
            "genotype": "not reported",
            "gene": "not reported",
            "assay": "not reported",
            "evidence_level": "unclassified",
            **overrides,
        }
    )
    return PhenotypeRecord.from_mapping(values)


def test_empty_templates_parse_without_records():
    csv_database = load_database(ATLAS / "phenotype_database.csv")
    json_database = load_database(ATLAS / "phenotype_database.json")
    assert csv_database.records == ()
    assert json_database.records == ()
    assert parse_source(ATLAS / "phenotype_database.csv") == ()


def test_empty_json_template_matches_schema():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((ATLAS / "phenotype_database.schema.json").read_text())
    document = json.loads((ATLAS / "phenotype_database.json").read_text())
    jsonschema.validate(document, schema)


def test_yaml_parser_reads_empty_records(tmp_path):
    source = tmp_path / "atlas.yaml"
    source.write_text("schema_version: '1.0'\nrecords: []\n", encoding="utf-8")
    assert parse_source(source) == ()


def test_provenance_never_infers_missing_pointers():
    provenance = Provenance.from_value({"paper": "P1", "figure": "Fig 1"})
    assert provenance.missing_fields() == ("table", "supplement", "page")
    assert Provenance.from_value("paper=P1;figure=Fig 1").paper == "P1"


def test_validation_reports_duplicate_ids_and_missing_information():
    first = _contract_record(doi="10.example/one", quality_score=1.2, evidence_level="invented")
    second = _contract_record(paper_id="contract-fixture-2", doi="10.example/one")
    report = validate_database((first, second))
    types = {issue["type"] for issue in report["issues"]}
    assert report["valid"] is False
    assert "DUPLICATE_DOI" in types
    assert "INVALID_QUALITY_SCORE" in types
    assert "INVALID_EVIDENCE_LEVEL" in types
    assert "MISSING_PROVENANCE" in types


def test_graph_and_search_use_declared_metadata_only():
    record = _contract_record(
        paper_id="contract-paper",
        gene="contract-gene",
        assay="contract-assay",
        year=2024,
        quality_score=0.8,
    )
    graph = build_knowledge_graph((record,))
    assert {node.node_type for node in graph.nodes} == {"paper", "gene", "assay"}
    assert find_by_gene((record,), "GENE") == (record,)
    assert find_by_assay((record,), "assay") == (record,)
    assert find_by_year((record,), 2024) == (record,)
    assert find_by_quality((record,), 0.75) == (record,)
    assert find_by_metric((record,), "walking_speed_mean") == ()
    with pytest.raises(ValueError):
        find_by_metric((record,), "unknown_metric")


def test_statistics_for_empty_template_are_explicit():
    statistics = build_statistics(())
    assert statistics["coverage"]["record_count"] == 0
    assert all(value == 0 for value in statistics["coverage"]["metric_coverage"].values())
    assert statistics["gene_summary"] == []
    assert statistics["quality_distribution"] == []


def test_report_generation_is_empty_data_safe(tmp_path):
    paths = write_atlas_report(PhenotypeDatabase(), tmp_path)
    expected = {
        "atlas_report.md",
        "atlas_report.json",
        "missing_information.md",
        "evidence_matrix.csv",
        "coverage_report.md",
        "coverage.json",
        "gene_summary.csv",
        "assay_summary.csv",
        "phenotype_summary.csv",
        "quality_distribution.csv",
    }
    assert {path.name for path in paths.values()} == expected
    payload = json.loads((tmp_path / "atlas_report.json").read_text(encoding="utf-8"))
    assert payload["record_count"] == 0
    assert "No records are present" in (tmp_path / "missing_information.md").read_text()


def test_database_json_round_trip_preserves_empty_template(tmp_path):
    database = load_database(ATLAS / "phenotype_database.json")
    destination = database.write_json(tmp_path / "round_trip.json")
    loaded = load_database(destination)
    assert loaded.records == ()
