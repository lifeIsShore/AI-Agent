import uuid
import time
from typing import Dict, Any, List, Optional

class EntityNode:
    def __init__(self, node_id: str, name: str, entity_type: str, metadata: Optional[Dict[str, Any]] = None):
        self.node_id = node_id
        self.name = name
        self.entity_type = entity_type # PERSON, PROJECT, GOAL, EMAIL, TASK, DOCUMENT
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "entity_type": self.entity_type,
            "metadata": self.metadata
        }

class RelationshipEdge:
    def __init__(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        confidence: float = 0.90,
        provenance_id: Optional[str] = None,
        valid_from: Optional[str] = None,
        valid_until: Optional[str] = None,
        source: Optional[str] = None,
        source_id_ref: Optional[str] = None,
        evidence: Optional[str] = None,
        supersedes_id: Optional[str] = None
    ):
        self.edge_id = f"edge_{uuid.uuid4().hex[:8]}"
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type # ADVISOR_OF, REQUIRES, BLOCKED_BY, DEADLINE, EMAILED, WORKS_ON
        self.confidence = confidence
        self.provenance_id = provenance_id or f"fact_{uuid.uuid4().hex[:8]}"
        
        # Interval Temporal Semantics (V6.7.1)
        self.valid_from = valid_from or "2026-04-01"
        self.valid_until = valid_until # None means currently active
        self.observed_at = time.strftime("%Y-%m-%d %H:%M:%S")

        # Graph-Native Provenance Metadata (V6.7.1)
        self.source = source or "GmailConnector"
        self.source_id_ref = source_id_ref or "msg_88192a"
        self.evidence = evidence or "Direct evidence statement from source observation."
        self.supersedes_id = supersedes_id

    def is_active(self) -> bool:
        return self.valid_until is None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "confidence": self.confidence,
            "provenance_id": self.provenance_id,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
            "observed_at": self.observed_at,
            "source": self.source,
            "source_id_ref": self.source_id_ref,
            "evidence": self.evidence,
            "supersedes_id": self.supersedes_id,
            "is_active": self.is_active()
        }

class PersonalKnowledgeGraph2:
    def __init__(self):
        self.nodes: Dict[str, EntityNode] = {}
        self.edges: List[RelationshipEdge] = []
        self._initialize_default_graph()

    def _initialize_default_graph(self):
        # Nodes
        self.add_node(EntityNode("n_ahmet", "Ahmet", "PERSON", {"role": "STUDENT_OWNER"}))
        self.add_node(EntityNode("n_davis", "Prof. Davis", "PERSON", {"role": "THESIS_ADVISOR"}))
        self.add_node(EntityNode("n_thesis", "Master Thesis", "PROJECT", {"status": "EXECUTING"}))
        self.add_node(EntityNode("n_msc", "M.Sc. Wirtschaftsinformatik", "GOAL", {"university": "Mannheim"}))
        self.add_node(EntityNode("n_methodology", "Thesis Methodology", "TASK", {"status": "IN_PROGRESS"}))

        # Edges with Interval Temporal & Provenance
        self.add_edge(RelationshipEdge("n_ahmet", "n_msc", "STUDIES", 0.99, valid_from="2024-09-01"))
        self.add_edge(RelationshipEdge("n_ahmet", "n_thesis", "WORKS_ON", 0.98, valid_from="2026-04-01"))
        self.add_edge(RelationshipEdge("n_davis", "n_thesis", "ADVISOR_OF", 0.95, valid_from="2026-04-01"))
        self.add_edge(RelationshipEdge("n_thesis", "n_methodology", "REQUIRES", 0.90, valid_from="2026-08-01"))

    def add_node(self, node: EntityNode):
        self.nodes[node.node_id] = node

    def add_edge(self, edge: RelationshipEdge):
        self.edges.append(edge)

    def get_graph_summary(self) -> Dict[str, Any]:
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "active_edges": sum(1 for e in self.edges if e.is_active()),
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges]
        }

class GraphReasoningEngine:
    def __init__(self, graph: PersonalKnowledgeGraph2):
        self.graph = graph

    def explain_importance(self, node_id: str) -> Dict[str, Any]:
        """Traverses active graph edges to explain why a node is currently important with provenance."""
        node = self.graph.nodes.get(node_id)
        if not node:
            return {"error": "Node not found"}

        connected_edges = [e for e in self.graph.edges if (e.source_id == node_id or e.target_id == node_id) and e.is_active()]

        return {
            "node": node.to_dict(),
            "connected_facts_count": len(connected_edges),
            "explanation": f"Entity '{node.name}' is connected to {len(connected_edges)} active mission relationships in knowledge graph.",
            "provenance_chain": [
                {
                    "provenance_id": e.provenance_id,
                    "source": e.source,
                    "valid_from": e.valid_from,
                    "evidence": e.evidence
                } for e in connected_edges
            ]
        }
