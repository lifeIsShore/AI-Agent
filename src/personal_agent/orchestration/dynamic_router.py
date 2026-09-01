from typing import Dict, Any, List, Tuple, Optional
from personal_agent.orchestration.roles import (
    ROLE_CONFIGS, ROLE_INBOX_ANALYST, ROLE_CALENDAR_PLANNER, ROLE_TASK_PLANNER
)

MODEL_TIER_RULES = "rules"
MODEL_TIER_LOCAL_SMALL = "local-small"
MODEL_TIER_LOCAL_MEDIUM = "local-medium"
MODEL_TIER_REMOTE_LARGE = "remote-large"

class DynamicStepRouter:
    def route_step_model(self, step_id: str, confidence: float, risk_level: str) -> Tuple[str, str]:
        """Routes model tier adaptively per step based on confidence score and risk level."""
        if risk_level == "HIGH" or confidence < 0.60:
            return MODEL_TIER_REMOTE_LARGE, f"Escalated step '{step_id}' to remote-large (Confidence: {confidence:.2f}, Risk: {risk_level})."
        elif confidence < 0.85:
            return MODEL_TIER_LOCAL_MEDIUM, f"Routed step '{step_id}' to local-medium (Confidence: {confidence:.2f})."
        elif confidence < 0.95:
            return MODEL_TIER_LOCAL_SMALL, f"Routed step '{step_id}' to local-small (Confidence: {confidence:.2f})."
        
        return MODEL_TIER_RULES, f"Routed step '{step_id}' to rule engine (Confidence: {confidence:.2f})."

class StepContextIsolator:
    def filter_context_for_role(self, role_name: str, full_context: Dict[str, Any]) -> Dict[str, Any]:
        """Isolates and filters context items to provide minimal required context per specialist role."""
        config = ROLE_CONFIGS.get(role_name)
        if not config:
            return full_context

        allowed_types = config.allowed_context_types
        filtered = {}
        
        for k, v in full_context.items():
            if k in allowed_types or k == "workflow_id":
                filtered[k] = v

        return filtered
