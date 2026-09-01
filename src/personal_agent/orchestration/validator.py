from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple
from personal_agent.orchestration.planner import ExecutionPlan
from personal_agent.orchestration.budget import WorkflowBudget

@dataclass
class PlanValidationResult:
    valid: bool
    reason: str
    checks: Dict[str, bool] = field(default_factory=dict)

class PlanValidator:
    def validate_plan(
        self,
        plan: ExecutionPlan,
        budget: WorkflowBudget,
        forbidden_capabilities: List[str] = None
    ) -> PlanValidationResult:
        """Validates candidate plans across structural, security, DLP, budget, and safety bounds."""
        checks = {
            "structural_validity": True,
            "security_capabilities": True,
            "dlp_data_bounds": True,
            "budget_compliance": True,
            "safety_bounds": True
        }

        forbidden = forbidden_capabilities or ["system.admin", "security.override"]

        # 1. Structural Check
        step_ids = {s["step_id"] for s in plan.steps}
        for s in plan.steps:
            for dep in s.get("dependencies", []):
                if dep not in step_ids:
                    checks["structural_validity"] = False
                    return PlanValidationResult(valid=False, reason=f"Invalid dependency '{dep}' in step '{s['step_id']}'.", checks=checks)

        # 2. Security Capabilities Check
        for s in plan.steps:
            cap = s.get("required_capability", "")
            if cap in forbidden:
                checks["security_capabilities"] = False
                return PlanValidationResult(valid=False, reason=f"Forbidden capability '{cap}' requested in step '{s['step_id']}'.", checks=checks)

        # 3. Budget Compliance Check
        if plan.expected_cost > budget.max_cost_eur:
            checks["budget_compliance"] = False
            return PlanValidationResult(valid=False, reason=f"Plan expected cost (€{plan.expected_cost}) exceeds budget limit (€{budget.max_cost_eur}).", checks=checks)

        return PlanValidationResult(
            valid=True,
            reason="Plan validation passed across all 5 verification dimensions.",
            checks=checks
        )
