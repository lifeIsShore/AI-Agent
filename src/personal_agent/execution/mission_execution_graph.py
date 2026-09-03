import uuid
import time
from typing import Dict, Any, List, Optional

class GraphNode:
    def __init__(
        self,
        node_id: str,
        name: str,
        node_type: str, # GOAL, MISSION, STRATEGY, TASK, AGENT, MODEL, ACTION
        owner: str = "System",
        status: str = "ACTIVE", # ACTIVE, EXECUTING, COMPLETED, BLOCKED
        deadline: Optional[str] = None,
        provenance_id: Optional[str] = None,
        authorization_state: str = "AUTHORIZED"
    ):
        self.node_id = node_id
        self.name = name
        self.node_type = node_type
        self.owner = owner
        self.status = status
        self.deadline = deadline or "2026-11-30"
        self.provenance_id = provenance_id or f"fact_{uuid.uuid4().hex[:8]}"
        self.authorization_state = authorization_state

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "node_type": self.node_type,
            "owner": self.owner,
            "status": self.status,
            "deadline": self.deadline,
            "provenance_id": self.provenance_id,
            "authorization_state": self.authorization_state
        }

class GraphEdge:
    def __init__(self, source_id: str, target_id: str, edge_type: str = "DEPENDS_ON"):
        self.source_id = source_id
        self.target_id = target_id
        self.edge_type = edge_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type
        }

class MissionExecutionGraph:
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self._initialize_canonical_graph()

    def _initialize_canonical_graph(self):
        # Goal -> Mission -> Strategy -> Task -> Agent -> Model -> Action
        n_goal = GraphNode("n_goal_thesis", "🎓 Master Thesis Proposal", "GOAL", "Ahmet", "ACTIVE")
        n_mission = GraphNode("n_mission_res", "Literature Synthesis Mission", "MISSION", "PlanningSpecialist", "EXECUTING")
        n_strategy = GraphNode("n_strat_c", "Strategy C (Iterative Critic)", "STRATEGY", "PredictiveOptimizer", "ACTIVE")
        n_task = GraphNode("n_task_lit", "Verify arXiv Contradictions", "TASK", "ResearchSpecialist", "EXECUTING")
        n_agent = GraphNode("n_agent_res", "ResearchSpecialist", "AGENT", "AgentMesh", "ACTIVE")
        n_model = GraphNode("n_model_cloud", "Strong Cloud LLM", "MODEL", "ModelRouter", "ACTIVE")
        n_action = GraphNode("n_action_search", "web_search", "ACTION", "ResearchSpecialist", "COMPLETED")

        for n in [n_goal, n_mission, n_strategy, n_task, n_agent, n_model, n_action]:
            self.add_node(n)

        self.add_edge(GraphEdge("n_goal_thesis", "n_mission_res", "DECOMPOSES_TO"))
        self.add_edge(GraphEdge("n_mission_res", "n_strat_c", "USES_STRATEGY"))
        self.add_edge(GraphEdge("n_strat_c", "n_task_lit", "REQUIRES_TASK"))
        self.add_edge(GraphEdge("n_task_lit", "n_agent_res", "ASSIGNED_TO"))
        self.add_edge(GraphEdge("n_agent_res", "n_model_cloud", "USES_MODEL"))
        self.add_edge(GraphEdge("n_model_cloud", "n_action_search", "EXECUTES_ACTION"))

    def add_node(self, node: GraphNode):
        self.nodes[node.node_id] = node

    def add_edge(self, edge: GraphEdge):
        self.edges.append(edge)

    def get_execution_summary(self) -> Dict[str, Any]:
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges]
        }
