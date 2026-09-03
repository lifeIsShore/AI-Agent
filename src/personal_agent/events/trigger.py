import uuid
from typing import Optional, Dict, Any, List
from personal_agent.events.event import AgentEvent
from personal_agent.workflow.models import Workflow, WorkflowStep, WF_CREATED

TRIGGER_RESPONSE_DEADLINE = "RESPONSE_DEADLINE_WARNING"
TRIGGER_SCHEDULE_CONFLICT = "SCHEDULE_CONFLICT_DETECTED"
TRIGGER_DEADLINE_WARNING = "TASK_DEADLINE_WARNING"

class TriggerEngine:
    def evaluate_triggers(
        self,
        events: List[AgentEvent],
        calendar_events: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Evaluates rule-based triggers from event streams."""
        triggers = []

        for e in events:
            payload = e.payload
            subj = str(payload.get("subject", payload.get("title", ""))).lower()
            event_type = e.event_type.upper()

            # 1. Response deadline warning trigger
            if payload.get("requires_action") and ("deadline" in subj or "urgent" in subj or "asap" in subj):
                triggers.append({
                    "trigger_id": TRIGGER_RESPONSE_DEADLINE,
                    "event_id": e.event_id,
                    "title": f"Response deadline warning for '{payload.get('subject', 'email')}'",
                    "risk": "HIGH",
                    "suggested_action": "create_task",
                    "reason": "Email indicates an urgent response deadline."
                })

            # 2. Schedule conflict trigger
            if event_type in ("CALENDAR_EVENT_CREATED", "CALENDAR_EVENT_UPDATED") or "room change" in subj or "conflict" in subj:
                if len(calendar_events) >= 1 or "conflict" in subj:
                    triggers.append({
                        "trigger_id": TRIGGER_SCHEDULE_CONFLICT,
                        "event_id": e.event_id,
                        "title": f"Schedule conflict detected for '{payload.get('summary', subj)}'",
                        "risk": "MEDIUM",
                        "suggested_action": "propose_schedule",
                        "reason": "Calendar change conflicts with existing schedule."
                    })

            # 3. Task deadline warning trigger
            if event_type == "DEADLINE_APPROACHING" or "deadline" in subj:
                triggers.append({
                    "trigger_id": TRIGGER_DEADLINE_WARNING,
                    "event_id": e.event_id,
                    "title": f"Task deadline warning: '{e.entity_id}'",
                    "risk": "HIGH",
                    "suggested_action": "propose_task",
                    "reason": "Task deadline is approaching."
                })

        return triggers

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
