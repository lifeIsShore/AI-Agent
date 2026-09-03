from typing import Dict, Any, Optional
from personal_agent.events.processor import EventProcessorResult
from personal_agent.events.deduplicator import EventDeduplicator
from personal_agent.runtime.supervisor import RuntimeSupervisor
from personal_agent.autonomy.governor import AutonomyGovernor

class ProactiveActionEngine:
    def __init__(
        self,
        supervisor: Optional[RuntimeSupervisor] = None,
        governor: Optional[AutonomyGovernor] = None,
        deduplicator: Optional[EventDeduplicator] = None
    ):
        self.supervisor = supervisor
        self.governor = governor or AutonomyGovernor()
        self.deduplicator = deduplicator or EventDeduplicator()

    def handle_event_result(
        self,
        result: EventProcessorResult,
        goal_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Evaluates EventProcessorResult and routes to appropriate outcome tier (IGNORE -> AUTONOMOUS_ACTION)."""
        if result.is_duplicate:
            return {
                "status": "DUPLICATE_SUPPRESSED",
                "event_id": result.event_id,
                "reason": result.details
            }

        outcome = result.recommended_outcome
        target_goal = goal_id
        if not target_goal and result.correlated_goals:
            target_goal = result.correlated_goals[0][0].goal_id
        target_goal = target_goal or "goal_autonomous_default"

        if outcome == "IGNORE":
            return {
                "status": "IGNORED",
                "event_id": result.event_id,
                "reason": result.details or "Low priority or non-actionable event."
            }

        elif outcome == "NOTIFY":
            return {
                "status": "NOTIFIED",
                "event_id": result.event_id,
                "action": result.action_type or "user_notification",
                "details": f"Notification generated for target {result.target_entity}."
            }

        elif outcome in ("RECOMMEND", "CREATE_TASK", "PROPOSE_ACTION"):
            return {
                "status": "PROPOSED",
                "event_id": result.event_id,
                "outcome_level": outcome,
                "action_type": result.action_type or "propose_task",
                "target": result.target_entity,
                "correlated_goal": target_goal
            }

        elif outcome == "AUTONOMOUS_ACTION":
            idem_key = f"idem_exec_{result.event_id}"
            
            # Idempotency check: Same event cannot execute autonomous action twice!
            if self.deduplicator.is_action_executed(idem_key):
                return {
                    "status": "IDEMPOTENT_SKIPPED",
                    "event_id": result.event_id,
                    "reason": f"Autonomous action for idempotency key '{idem_key}' already executed."
                }

            action_name = result.action_type or "get_current_time"

            # Execute via RuntimeSupervisor (if available) or evaluate via AutonomyGovernor
            if self.supervisor:
                exec_res = self.supervisor.execute_autonomous_action(
                    goal_id=target_goal,
                    proposed_action=action_name,
                    risk_level="LOW"
                )
                if exec_res.get("status") == "SUCCESS":
                    self.deduplicator.record_execution(idem_key)
                return exec_res
            else:
                # Direct Governor check
                auth_ok, auth_msg = self.governor.authorize_action(
                    action=action_name,
                    target=result.target_entity or "system",
                    risk="LOW",
                    autonomy_level="LEVEL_3_BOUNDED_AUTO"
                )
                if auth_ok:
                    self.deduplicator.record_execution(idem_key)
                    return {
                        "status": "SUCCESS",
                        "event_id": result.event_id,
                        "action_taken": action_name,
                        "governor_msg": auth_msg
                    }
                else:
                    return {
                        "status": "DENIED",
                        "event_id": result.event_id,
                        "reason": auth_msg
                    }

        return {
            "status": "UNKNOWN_OUTCOME",
            "event_id": result.event_id,
            "outcome": outcome
        }
