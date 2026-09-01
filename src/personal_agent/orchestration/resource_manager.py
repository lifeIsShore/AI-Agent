import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, Optional
from personal_agent.orchestration.budget import WorkflowBudget

@dataclass
class ResourceReservation:
    reservation_id: str
    workflow_id: str
    est_tokens: int
    est_cost: float
    est_tool_calls: int
    status: str = "PENDING"  # PENDING | COMMITTED | RELEASED

class ResourceManager:
    def __init__(self, global_budget: Optional[WorkflowBudget] = None):
        self.budget = global_budget or WorkflowBudget()
        self.reservations: Dict[str, ResourceReservation] = {}

    def reserve(
        self,
        workflow_id: str,
        est_tokens: int,
        est_cost: float,
        est_tool_calls: int = 1
    ) -> Tuple[bool, str, str]:
        """Performs pre-execution resource reservation check."""
        projected_tokens = self.budget.current_tokens + est_tokens
        projected_cost = self.budget.current_cost_eur + est_cost
        projected_tool_calls = self.budget.current_tool_calls + est_tool_calls

        if projected_tokens > self.budget.max_tokens:
            return False, "", f"Resource reservation rejected: Token limit exceeded ({projected_tokens} > {self.budget.max_tokens})."
        if projected_cost > self.budget.max_cost_eur:
            return False, "", f"Resource reservation rejected: Cost limit exceeded (€{projected_cost:.4f} > €{self.budget.max_cost_eur:.2f})."
        if projected_tool_calls > self.budget.max_tool_calls:
            return False, "", f"Resource reservation rejected: Tool call limit exceeded ({projected_tool_calls} > {self.budget.max_tool_calls})."

        res_id = f"res_{uuid.uuid4().hex[:8]}"
        res = ResourceReservation(
            reservation_id=res_id,
            workflow_id=workflow_id,
            est_tokens=est_tokens,
            est_cost=est_cost,
            est_tool_calls=est_tool_calls
        )
        self.reservations[res_id] = res
        return True, res_id, f"Resource reservation '{res_id}' granted for workflow '{workflow_id}'."

    def commit(
        self,
        reservation_id: str,
        actual_tokens: int,
        actual_cost: float,
        actual_runtime: float,
        actual_tool_calls: int = 1
    ) -> Tuple[bool, str]:
        """Commits actual resource usage to budget counter."""
        res = self.reservations.get(reservation_id)
        if not res or res.status != "PENDING":
            return False, f"Reservation '{reservation_id}' invalid or already settled."

        res.status = "COMMITTED"
        ok, msg = self.budget.record_usage(
            tokens=actual_tokens,
            cost=actual_cost,
            runtime=actual_runtime,
            tool_calls=actual_tool_calls
        )
        return ok, f"Reservation '{reservation_id}' committed successfully. Budget: {msg}"

    def release(self, reservation_id: str) -> Tuple[bool, str]:
        """Releases pending reservation upon cancelled/aborted execution."""
        res = self.reservations.get(reservation_id)
        if not res or res.status != "PENDING":
            return False, f"Reservation '{reservation_id}' invalid."

        res.status = "RELEASED"
        return True, f"Reservation '{reservation_id}' released."
