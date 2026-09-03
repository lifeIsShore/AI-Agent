from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from personal_agent.events.event import AgentEvent
from personal_agent.events.deduplicator import EventDeduplicator
from personal_agent.events.goal_correlator import EventGoalCorrelator
from personal_agent.events.trigger import TriggerEngine
from personal_agent.goals.goal import Goal

@dataclass
class EventProcessorResult:
    event_id: str
    is_duplicate: bool
    correlated_goals: List[Tuple[Goal, str, float]] = field(default_factory=list)
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    recommended_outcome: str = "IGNORE"  # IGNORE, NOTIFY, RECOMMEND, CREATE_TASK, PROPOSE_ACTION, AUTONOMOUS_ACTION
    action_type: Optional[str] = None
    target_entity: Optional[str] = None
    details: str = ""

class EventProcessor:
    def __init__(
        self,
        deduplicator: Optional[EventDeduplicator] = None,
        goal_correlator: Optional[EventGoalCorrelator] = None,
        trigger_engine: Optional[TriggerEngine] = None
    ):
        self.deduplicator = deduplicator or EventDeduplicator()
        self.goal_correlator = goal_correlator or EventGoalCorrelator()
        self.trigger_engine = trigger_engine or TriggerEngine()

    def process_event(
        self,
        event: AgentEvent,
        active_goals: Optional[List[Goal]] = None,
        calendar_events: Optional[List[Dict[str, Any]]] = None,
        tasks: Optional[List[Dict[str, Any]]] = None
    ) -> EventProcessorResult:
        """Processes event through deterministic rule-first pipeline: Deduplicate -> Correlate -> Trigger -> Propose."""
        # 1. Deduplication check
        is_dup, dup_msg = self.deduplicator.is_duplicate(event)
        if is_dup:
            return EventProcessorResult(
                event_id=event.event_id,
                is_duplicate=True,
                recommended_outcome="IGNORE",
                details=dup_msg
            )

        goals = active_goals or []
        cal = calendar_events or []
        tsk = tasks or []

        # 2. Goal Correlation
        correlations = self.goal_correlator.correlate_event_to_goals(event, goals)

        # 3. Trigger Engine Evaluation
        triggers = self.trigger_engine.evaluate_triggers([event], cal, tsk)

        # 4. Outcome Determination (Rule-First)
        outcome = "IGNORE"
        action_type = None
        target_entity = event.entity_id

        # High/Urgent priority or direct action requirement
        req_action = event.payload.get("requires_action", False)
        req_plan = event.payload.get("requires_planning", False)
        sender = str(event.payload.get("sender", "")).lower()
        subject = str(event.payload.get("subject", "")).lower()

        if triggers:
            top_trigger = triggers[0]
            if top_trigger.get("risk") in ("HIGH", "URGENT"):
                outcome = "AUTONOMOUS_ACTION" if event.payload.get("allow_auto", False) else "PROPOSE_ACTION"
                action_type = top_trigger.get("suggested_action", "create_task")
            else:
                outcome = "RECOMMEND"
                action_type = "propose_schedule"

        elif req_action and req_plan:
            if any(k in sender for k in ("prof", "advisor", "bank")) or any(k in subject for k in ("urgent", "asap", "deadline")):
                outcome = "AUTONOMOUS_ACTION" if event.payload.get("allow_auto", False) else "PROPOSE_ACTION"
                action_type = "create_task"
            else:
                outcome = "RECOMMEND"
                action_type = "create_task"

        elif req_action:
            outcome = "NOTIFY"
            action_type = "notify_user"

        elif correlations and correlations[0][2] >= 0.7:
            outcome = "NOTIFY"
            action_type = "update_goal_context"

        return EventProcessorResult(
            event_id=event.event_id,
            is_duplicate=False,
            correlated_goals=correlations,
            triggers=triggers,
            recommended_outcome=outcome,
            action_type=action_type,
            target_entity=target_entity,
            details=f"Processed event '{event.event_type}' successfully."
        )
