import uuid
from typing import Optional, Dict, Any
from personal_agent.workflow.models import Workflow, WorkflowStep, WF_CREATED

class ProactiveTriggerEngine:
    def evaluate_proactive_trigger(
        self,
        event_payload: Dict[str, Any],
        priority: str
    ) -> Optional[Workflow]:
        """Translates high-priority events (P4/P5) into candidate workflows subject to policy authorization."""
        if priority not in ["P4", "P5"]:
            return None

        subject = str(event_payload.get("subject", event_payload.get("summary", "")))
        wf_id = f"wf_proactive_{uuid.uuid4().hex[:8]}"

        steps = [
            WorkflowStep(step_id="step_1_inspect", objective=f"Inspect event context for '{subject}'", required_capabilities=["system.read"]),
            WorkflowStep(step_id="step_2_proposal", objective=f"Formulate proactive proposal for '{subject}'", dependencies=["step_1_inspect"], required_capabilities=["calendar.create"])
        ]

        return Workflow(
            workflow_id=wf_id,
            objective=f"Proactive handling: {subject}",
            priority="HIGH" if priority == "P5" else "NORMAL",
            steps=steps,
            status=WF_CREATED
        )
