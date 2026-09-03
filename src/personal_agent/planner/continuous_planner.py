from typing import Dict, Any, Optional, List
from personal_agent.context.situation_model import SituationModel, CurrentSituation
from personal_agent.goals.arbitration import GoalArbitrator
from personal_agent.planner.replanning_policy import ReplanningPolicy
from personal_agent.planner.resource_planner import ResourceAwarePlanner
from personal_agent.autonomy.proactivity_budget import ProactivityBudget
from personal_agent.runtime.supervisor import RuntimeSupervisor
from personal_agent.autonomy.governor import AutonomyGovernor
from personal_agent.events.event import AgentEvent

class ContinuousPlanner:
    def __init__(
        self,
        situation_model: Optional[SituationModel] = None,
        replanning_policy: Optional[ReplanningPolicy] = None,
        goal_arbitrator: Optional[GoalArbitrator] = None,
        resource_planner: Optional[ResourceAwarePlanner] = None,
        budget: Optional[ProactivityBudget] = None,
        supervisor: Optional[RuntimeSupervisor] = None,
        governor: Optional[AutonomyGovernor] = None
    ):
        self.situation_model = situation_model or SituationModel()
        self.replanning_policy = replanning_policy or ReplanningPolicy()
        self.goal_arbitrator = goal_arbitrator or GoalArbitrator()
        self.resource_planner = resource_planner or ResourceAwarePlanner()
        self.budget = budget or ProactivityBudget()
        self.supervisor = supervisor
        self.governor = governor or AutonomyGovernor()

    def evaluate_and_replan(
        self,
        event: AgentEvent,
        situation: CurrentSituation
    ) -> Dict[str, Any]:
        """Continuously evaluates situation delta and replans schedule subject to policy & supervisor rules."""
        # 1. Supervisor runtime state check (Hard Security Invariant)
        if self.supervisor and self.supervisor.current_state.value != "RUNNING":
            reason_msg = f"Continuous Planner BLOCKED. Supervisor state is '{self.supervisor.current_state.value}' (must be RUNNING)."
            print(f"[ContinuousPlanner SAFETY GATE] {reason_msg}")
            return {
                "status": "BLOCKED",
                "reason": reason_msg,
                "supervisor_state": self.supervisor.current_state.value
            }

        # 2. Materiality check via ReplanningPolicy
        should_replan, replan_reason = self.replanning_policy.should_replan(event, situation)
        if not should_replan:
            return {
                "status": "NO_REPLAN_NEEDED",
                "event_id": event.event_id,
                "reason": replan_reason
            }

        # 3. Proactivity Budget replan cap check
        can_replan, budget_msg = self.budget.can_replan()
        if not can_replan:
            return {
                "status": "BUDGET_EXCEEDED",
                "event_id": event.event_id,
                "reason": budget_msg
            }

        # 4. Arbitrate Goals with Starvation Prevention
        scored_goals = self.goal_arbitrator.select_prioritized_goals(situation.active_goals)
        top_goal = scored_goals[0][0] if scored_goals else None
        top_goal_id = top_goal.goal_id if top_goal else "default_goal"

        # 5. Resource-Aware Allocation (Non-overlapping free calendar slots)
        scheduled_blocks = self.resource_planner.allocate_task_schedules(
            tasks=situation.tasks,
            calendar_events=situation.calendar_events
        )

        # Record replan in budget
        self.budget.record_replan()

        # 6. Formulate Proactive Output (Notification or Action Proposal)
        proactive_output = None
        if event.payload.get("allow_auto", False) and top_goal:
            can_auto, auto_msg = self.budget.can_execute_auto_action()
            if can_auto:
                if self.supervisor:
                    exec_res = self.supervisor.execute_autonomous_action(
                        goal_id=top_goal_id,
                        proposed_action="get_current_time",
                        risk_level="LOW"
                    )
                    if exec_res.get("status") == "SUCCESS":
                        self.budget.record_auto_action()
                    proactive_output = exec_res
                else:
                    self.budget.record_auto_action()
                    proactive_output = {"status": "SUCCESS", "action_taken": "get_current_time"}
            else:
                proactive_output = {"status": "BUDGET_EXCEEDED", "reason": auto_msg}
        else:
            can_notify, notify_msg = self.budget.can_notify(goal_id=top_goal_id)
            if can_notify:
                self.budget.record_notification(goal_id=top_goal_id)
                proactive_output = {
                    "status": "NOTIFIED",
                    "goal_id": top_goal_id,
                    "message": f"Proactive plan update for '{top_goal.objective if top_goal else 'schedule'}': {replan_reason}"
                }
            else:
                proactive_output = {"status": "BUDGET_EXCEEDED", "reason": notify_msg}

        return {
            "status": "REPLANNED",
            "event_id": event.event_id,
            "replan_reason": replan_reason,
            "top_prioritized_goal": top_goal.objective if top_goal else None,
            "top_goal_id": top_goal_id,
            "scheduled_blocks_count": len(scheduled_blocks),
            "scheduled_blocks": scheduled_blocks,
            "proactive_output": proactive_output
        }
