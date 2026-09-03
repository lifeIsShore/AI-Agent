from typing import Dict, Any, List

class WorldModelConsolidator:
    def consolidate_world_graph(
        self,
        entities: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Consolidates cross-domain relationships into a durable world model graph."""
        entity_map: Dict[str, Dict[str, Any]] = {e["id"]: e for e in entities if "id" in e}
        graph_edges: List[Dict[str, Any]] = []

        for rel in relationships:
            src = rel.get("source_id")
            tgt = rel.get("target_id")
            rel_type = rel.get("relation_type", "RELATED_TO")

            if src in entity_map and tgt in entity_map:
                graph_edges.append({
                    "source": entity_map[src],
                    "target": entity_map[tgt],
                    "relation": rel_type,
                    "strength": rel.get("strength", 1.0)
                })

        return {
            "status": "CONSOLIDATED",
            "total_entities": len(entity_map),
            "total_relationships": len(graph_edges),
            "graph_edges": graph_edges
        }
