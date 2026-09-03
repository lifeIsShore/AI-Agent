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
        provenance_id: Optional[str] = None
    ):
        self.edge_id = f"edge_{uuid.uuid4().hex[:8]}"
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type # ADVISOR_OF, REQUIRES, BLOCKED_BY, DEADLINE, EMAILED, WORKS_ON
        self.confidence = confidence
        self.provenance_id = provenance_id or f"fact_{uuid.uuid4().hex[:8]}"
        self.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.end_time = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "confidence": self.confidence,
            "provenance_id": self.provenance_id,
            "start_time": self.start_time,
            "end_time": self.end_time
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

        # Edges
        self.add_edge(RelationshipEdge("n_ahmet", "n_msc", "STUDIES", 0.99))
        self.add_edge(RelationshipEdge("n_ahmet", "n_thesis", "WORKS_ON", 0.98))
        self.add_edge(RelationshipEdge("n_davis", "n_thesis", "ADVISOR_OF", 0.95))
        self.add_edge(RelationshipEdge("n_thesis", "n_methodology", "REQUIRES", 0.90))

    def add_node(self, node: EntityNode):
        self.nodes[node.node_id] = node

    def add_edge(self, edge: RelationshipEdge):
        self.edges.append(edge)

    def get_graph_summary(self) -> Dict[str, Any]:
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges]
        }

class GraphReasoningEngine:
    def __init__(self, graph: PersonalKnowledgeGraph2):
        self.graph = graph

    def explain_importance(self, node_id: str) -> Dict[str, Any]:
        """Traverses graph edges to explain why a node is currently important."""
        node = self.graph.nodes.get(node_id)
        if not node:
            return {"error": "Node not found"}

        connected_edges = [e for e in self.graph.edges if e.source_id == node_id or e.target_id == node_id]

        return {
            "node": node.to_dict(),
            "connected_facts_count": len(connected_edges),
            "explanation": f"Entity '{node.name}' is connected to {len(connected_edges)} core mission relationships in knowledge graph.",
            "provenance_chain": [e.provenance_id for e in connected_edges]
        }
