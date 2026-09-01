import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

@dataclass
class WorkflowContext:
    workflow_id: str
    goal: str
    created_at: str
    status: str                        # ACTIVE | COMPLETED | FAILED
    request_ids: List[str] = field(default_factory=list)
    proposal_ids: List[str] = field(default_factory=list)

class WorkflowEngine:
    def __init__(self):
        self.workflows: Dict[str, WorkflowContext] = {}

    def start_workflow(self, goal: str) -> WorkflowContext:
        """Creates new top-level workflow context with unique workflow_id."""
        wf_id = f"wf_{uuid.uuid4().hex[:8]}"
        wf = WorkflowContext(
            workflow_id=wf_id,
            goal=goal,
            created_at=datetime.now(timezone.utc).isoformat(),
            status="ACTIVE",
            request_ids=[],
            proposal_ids=[]
        )
        self.workflows[wf_id] = wf
        return wf

    def link_request(self, workflow_id: str, request_id: str):
        if workflow_id in self.workflows:
            self.workflows[workflow_id].request_ids.append(request_id)

    def link_proposal(self, workflow_id: str, proposal_id: str):
        if workflow_id in self.workflows:
            self.workflows[workflow_id].proposal_ids.append(proposal_id)

    def get_workflow_lineage(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        wf = self.workflows.get(workflow_id)
        if not wf:
            return None
        return {
            "workflow_id": wf.workflow_id,
            "goal": wf.goal,
            "status": wf.status,
            "created_at": wf.created_at,
            "linked_requests": wf.request_ids,
            "linked_proposals": wf.proposal_ids
        }
