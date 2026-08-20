"""Small in-memory knowledge graph for curated atlas relationships."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .models import PhenotypeRecord


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    node_type: str
    label: str

    def to_mapping(self) -> dict[str, str]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "label": self.label,
        }


@dataclass(frozen=True)
class GraphEdge:
    source: str
    relation: str
    target: str

    def to_mapping(self) -> dict[str, str]:
        return {
            "source": self.source,
            "relation": self.relation,
            "target": self.target,
        }


@dataclass(frozen=True)
class KnowledgeGraph:
    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...]

    def to_mapping(self) -> dict[str, Any]:
        return {
            "nodes": [node.to_mapping() for node in self.nodes],
            "edges": [edge.to_mapping() for edge in self.edges],
        }


def build_knowledge_graph(records: Iterable[PhenotypeRecord]) -> KnowledgeGraph:
    """Build Paper -> Gene -> Phenotype -> Assay -> Metric -> Evidence links."""

    nodes: dict[str, GraphNode] = {}
    edges: set[GraphEdge] = set()

    def add_node(node_type: str, label: str) -> str:
        node_id = f"{node_type}:{label}"
        nodes.setdefault(node_id, GraphNode(node_id, node_type, label))
        return node_id

    def add_edge(source: str, relation: str, target: str) -> None:
        edges.add(GraphEdge(source, relation, target))

    for record in records:
        paper = record.paper_id
        if not paper:
            continue
        paper_id = add_node("paper", paper)
        gene_value = str(record.get("gene") or "").strip()
        if gene_value:
            gene_id = add_node("gene", gene_value)
            add_edge(paper_id, "reports_gene", gene_id)
        assay_value = str(record.get("assay") or "").strip()
        assay_id = add_node("assay", assay_value) if assay_value else None
        for metric in record.populated_metrics():
            phenotype_id = add_node("phenotype", metric)
            metric_id = add_node("metric", metric)
            evidence_id = add_node("evidence", f"{paper}:{metric}")
            add_edge(paper_id, "reports_phenotype", phenotype_id)
            if assay_id:
                add_edge(phenotype_id, "measured_by", assay_id)
            add_edge(phenotype_id, "uses_metric", metric_id)
            add_edge(metric_id, "supported_by", evidence_id)
    return KnowledgeGraph(tuple(sorted(nodes.values(), key=lambda item: item.node_id)), tuple(sorted(edges, key=lambda item: (item.source, item.relation, item.target))))


__all__ = ["GraphEdge", "GraphNode", "KnowledgeGraph", "build_knowledge_graph"]
