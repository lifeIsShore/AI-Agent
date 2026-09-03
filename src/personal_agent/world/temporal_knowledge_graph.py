import uuid
from typing import Dict, Any, List, Optional

class TemporalKnowledgeGraph:
    def __init__(self):
        self.nodes: List[Dict[str, Any]] = [
            {"node_id": "t_2026_bsc", "year": 2026, "event_name": "B.Sc. Business Information Systems Completed", "category": "EDUCATION", "status": "COMPLETED"},
            {"node_id": "t_2026_msc", "year": 2026, "event_name": "M.Sc. Wirtschaftsinformatik Started", "category": "EDUCATION", "status": "ACTIVE"},
            {"node_id": "t_2026_thesis", "year": 2026, "event_name": "Master Thesis Proposal & Research", "category": "RESEARCH", "status": "ACTIVE"}
        ]

    def add_timeline_node(
        self,
        year: int,
        event_name: str,
        category: str,
        status: str = "COMPLETED"
    ) -> Dict[str, Any]:
        node = {
            "node_id": f"t_{year}_{uuid.uuid4().hex[:6]}",
            "year": year,
            "event_name": event_name,
            "category": category,
            "status": status
        }
        self.nodes.append(node)
        return node

    def get_timeline(self, start_year: Optional[int] = None) -> List[Dict[str, Any]]:
        if start_year is None:
            return sorted(self.nodes, key=lambda x: (x["year"], x["node_id"]))
        return sorted([n for n in self.nodes if n["year"] >= start_year], key=lambda x: (x["year"], x["node_id"]))

    def reason_over_timeline(self) -> Dict[str, Any]:
        """Reasons over what happened -> what changed -> why it changed -> what is currently relevant -> what is likely to happen next."""
        timeline = self.get_timeline()
        active_nodes = [n for n in timeline if n.get("status") == "ACTIVE"]

        return {
            "timeline_length": len(timeline),
            "past_milestones": [n["event_name"] for n in timeline if n.get("status") == "COMPLETED"],
            "currently_active": [n["event_name"] for n in active_nodes],
            "why_changed": "Graduated B.Sc. with grade 2.0/thesis 1.3 -> transitioned to M.Sc. Wirtschaftsinformatik at University of Mannheim.",
            "next_likely_event": "Master Thesis Submission & Internship Selection"
        }
