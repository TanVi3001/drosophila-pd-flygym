from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from drosophila_pd.literature_assistant.candidate import CandidatePhenotype
from drosophila_pd.literature_assistant.parser import ParserError, parse_source
from drosophila_pd.literature_assistant.report import write_review_reports
from drosophila_pd.literature_assistant.review import ReviewStatus, ReviewStore
from drosophila_pd.literature_assistant.validation import validate_candidate, validate_candidates
from drosophila_pd.literature_assistant.workflow import LiteratureAssistantWorkflow


def _candidate(**overrides) -> CandidatePhenotype:
    values = {
        "candidate_id": "contract_candidate",
        "paper_id": "contract-paper",
        "citation": "Contract fixture, not a scientific observation",
        "doi": "10.example/contract",
        "gene": "not reported",
        "genotype": "not reported",
        "species": "not reported",
        "assay": "contract assay",
        "walking_speed": 1.0,
        "walking_speed_unit": "contract-unit",
        "stride": 2.0,
        "stride_unit": "contract-unit",
        "sample_size": 1,
        "figure_reference": "Fig. contract",
        "table_reference": "Table contract",
        "supplementary_reference": "Supplement contract",
        "page": "1",
        "confidence": 0.5,
        "notes": "Test contract only; not evidence.",
    }
    values.update(overrides)
    return CandidatePhenotype.from_mapping(values)


def test_parser_reads_only_explicit_markdown_fields(tmp_path):
    source = tmp_path / "paper.md"
    source.write_text(
        "A prose paragraph with no structured candidate.\n\n"
        "[candidate]\n"
        "candidate_id: paper_001\n"
        "gene: not reported\n"
        "assay: contract assay\n"
        "walking_speed: 1.5\n"
        "walking_speed_unit: mm/s\n",
        encoding="utf-8",
    )
    candidates = parse_source(source)
    assert len(candidates) == 1
    assert candidates[0].candidate_id == "paper_001"
    assert candidates[0].get("walking_speed") == 1.5
    assert candidates[0].get("manual_review_required") is True


def test_parser_reads_csv_and_rejects_unsupported_type(tmp_path):
    source = tmp_path / "candidates.csv"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "assay"])
        writer.writeheader()
        writer.writerow({"id": "csv_001", "assay": "contract assay"})
    assert parse_source(source)[0].candidate_id == "csv_001"
    unsupported = tmp_path / "paper.docx"
    unsupported.write_text("not supported", encoding="utf-8")
    with pytest.raises(ParserError):
        parse_source(unsupported)


def test_validation_reports_provenance_assay_unit_and_duplicate_doi():
    incomplete = CandidatePhenotype.from_mapping({"candidate_id": "incomplete"})
    report = validate_candidate(incomplete)
    codes = {issue["code"] for issue in report["issues"]}
    assert {"MISSING_PROVENANCE", "MISSING_FIGURE", "MISSING_ASSAY"} <= codes
    duplicate = _candidate(candidate_id="duplicate")
    duplicate_report = validate_candidates((_candidate(), duplicate))
    assert duplicate_report["valid"] is False
    assert any(issue["code"] == "DUPLICATE_DOI" for issue in duplicate_report["issues"])


def test_review_lifecycle_requires_approval_and_edit_resets_pending(tmp_path):
    store = ReviewStore([_candidate()])
    assert store.status_for("contract_candidate") is ReviewStatus.PENDING
    assert store.approved_records() == ()
    store.approve("contract_candidate", reviewer="researcher", comment="Contract review")
    assert store.status_for("contract_candidate") is ReviewStatus.APPROVED
    assert len(store.approved_records()) == 1
    store.edit("contract_candidate", {"notes": "Edited by curator"}, reviewer="researcher")
    assert store.status_for("contract_candidate") is ReviewStatus.PENDING
    assert store.approved_records() == ()
    store.reject("contract_candidate", reviewer="researcher", comment="Not usable")
    assert store.status_for("contract_candidate") is ReviewStatus.REJECTED
    review_path = store.write_json(tmp_path / "candidate_review.json")
    payload = json.loads(review_path.read_text(encoding="utf-8"))
    assert set(payload) >= {"schema_version", "candidates", "reviews"}
    assert not (tmp_path / "phenotype_database.csv").exists()


def test_review_cannot_approve_duplicate_doi():
    store = ReviewStore([_candidate(), _candidate(candidate_id="duplicate")])
    with pytest.raises(ValueError, match="DUPLICATE_DOI"):
        store.approve("contract_candidate", reviewer="researcher")


def test_workflow_persists_queue_and_reports_only_review_states(tmp_path):
    source = tmp_path / "source.csv"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(_candidate().to_mapping()))
        writer.writeheader()
        writer.writerow(_candidate().to_mapping())
    workflow = LiteratureAssistantWorkflow(tmp_path / "review")
    outputs = workflow.run([source])
    assert (tmp_path / "review" / "candidate_review.json").is_file()
    assert {path.name for path in outputs.values()} == {"review_summary.md", "approved.csv", "rejected.csv", "pending.csv"}
    assert "Pending: 1" in outputs["summary"].read_text(encoding="utf-8")
    workflow.approve("contract_candidate", reviewer="researcher")
    approved = workflow.export_approved()
    assert approved[0].paper_id == "contract-paper"
    workflow.write_reports()
    with (tmp_path / "review" / "approved.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1


def test_report_generation_has_stable_empty_status_files(tmp_path):
    paths = write_review_reports(ReviewStore(), tmp_path)
    assert set(paths) == {"summary", "approved", "rejected", "pending"}
    assert "Candidates: 0" in paths["summary"].read_text(encoding="utf-8")
