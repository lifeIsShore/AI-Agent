import os
import json
import time
import uuid
import tempfile
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from personal_agent.workflow.dag import WorkflowDAG

@dataclass
class WorkflowCheckpoint:
    checkpoint_id: str
    goal_id: str
    dag_id: str
    completed_node_ids: List[str] = field(default_factory=list)
    active_node_id: Optional[str] = None
    failed_node_ids: List[str] = field(default_factory=list)
    progress_pct: float = 0.0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowCheckpoint":
        return cls(
            checkpoint_id=data.get("checkpoint_id", f"wf_chk_{uuid.uuid4().hex[:8]}"),
            goal_id=data.get("goal_id", "g_default"),
            dag_id=data.get("dag_id", "dag_default"),
            completed_node_ids=data.get("completed_node_ids", []),
            active_node_id=data.get("active_node_id"),
            failed_node_ids=data.get("failed_node_ids", []),
            progress_pct=data.get("progress_pct", 0.0),
            timestamp=data.get("timestamp", time.time()),
            metadata=data.get("metadata", {})
        )

class WorkflowCheckpointManager:
    def __init__(self, storage_dir: str = "data/workflows", filename: str = "checkpoint.json"):
        self.storage_dir = os.path.abspath(storage_dir)
        self.filepath = os.path.join(self.storage_dir, filename)
        os.makedirs(self.storage_dir, exist_ok=True)

    def save_checkpoint(
        self,
        goal_id: str,
        workflow_or_dag: Any,
        active_node_id: Optional[str] = None,
        progress_pct: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorkflowCheckpoint:
        if hasattr(workflow_or_dag, "steps"):
            completed = [s.step_id for s in workflow_or_dag.steps if s.status == "COMPLETED"]
            failed = [s.step_id for s in workflow_or_dag.steps if s.status == "FAILED"]
            dag_id = getattr(workflow_or_dag, "workflow_id", "wf_default")
        elif hasattr(workflow_or_dag, "nodes"):
            completed = [nid for nid, node in workflow_or_dag.nodes.items() if getattr(node, "status", "") == "COMPLETED"]
            failed = [nid for nid, node in workflow_or_dag.nodes.items() if getattr(node, "status", "") == "FAILED"]
            dag_id = getattr(workflow_or_dag, "dag_id", "dag_default")
        else:
            completed = []
            failed = []
            dag_id = "wf_default"

        chk = WorkflowCheckpoint(
            checkpoint_id=f"wf_chk_{uuid.uuid4().hex[:8]}",
            goal_id=goal_id,
            dag_id=dag_id,
            completed_node_ids=completed,
            active_node_id=active_node_id,
            failed_node_ids=failed,
            progress_pct=progress_pct,
            timestamp=time.time(),
            metadata=metadata or {}
        )

        temp_fd, temp_path = tempfile.mkstemp(dir=self.storage_dir, prefix="wf_chk_tmp_", suffix=".json")
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(chk.to_dict(), f, indent=2)
            os.replace(temp_path, self.filepath)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            print(f"[WorkflowCheckpointManager ERROR] Failed to save workflow checkpoint: {e}")

        return chk

    def load_checkpoint(self) -> Optional[WorkflowCheckpoint]:
        if not os.path.exists(self.filepath):
            return None
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return WorkflowCheckpoint.from_dict(data)
        except Exception as e:
            print(f"[WorkflowCheckpointManager WARNING] Failed to load checkpoint: {e}. Returning None.")
            return None
