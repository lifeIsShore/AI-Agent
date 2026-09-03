import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from personal_agent.goals.goal import Goal
from personal_agent.events.event import AgentEvent

@dataclass
class CurrentSituation:
    situation_id: str
    timestamp: float
    active_goals: List[Goal] = field(default_factory=list)
    active_workflows: List[Any] = field(default_factory=list)
    recent_events: List[AgentEvent] = field(default_factory=list)
    calendar_events: List[Dict[str, Any]] = field(default_factory=list)
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    deadlines: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "situation_id": self.situation_id,
            "timestamp": self.timestamp,
            "active_goals_count": len(self.active_goals),
            "recent_events_count": len(self.recent_events),
            "calendar_events_count": len(self.calendar_events),
            "tasks_count": len(self.tasks),
            "deadlines_count": len(self.deadlines),
            "constraints": self.constraints
        }

class SituationModel:
    def build_situation(
        self,
        goals: Optional[List[Goal]] = None,
        workflows: Optional[List[Any]] = None,
        events: Optional[List[AgentEvent]] = None,
        calendar_events: Optional[List[Dict[str, Any]]] = None,
        tasks: Optional[List[Dict[str, Any]]] = None,
        constraints: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CurrentSituation:
        """Aggregates active domain entities into a cohesive situational snapshot."""
        g_list = goals or []
        wf_list = workflows or []
        e_list = events or []
        cal_list = calendar_events or []
        t_list = tasks or []
        c_list = constraints or []

        # Extract deadlines from goals and tasks
        deadlines = []
        for g in g_list:
            if g.deadline:
                deadlines.append({"type": "goal", "id": g.goal_id, "title": g.objective, "deadline": g.deadline, "priority": g.priority})
        for t in t_list:
            if t.get("deadline") or t.get("due_date"):
                deadlines.append({"type": "task", "id": str(t.get("task_id", t.get("id"))), "title": str(t.get("title", t.get("subject"))), "deadline": t.get("deadline") or t.get("due_date"), "priority": t.get("priority", "NORMAL")})

        return CurrentSituation(
            situation_id=f"sit_{uuid.uuid4().hex[:8]}",
            timestamp=time.time(),
            active_goals=g_list,
            active_workflows=wf_list,
            recent_events=e_list,
            calendar_events=cal_list,
            tasks=t_list,
            deadlines=deadlines,
            constraints=c_list,
            metadata=metadata or {}
        )
