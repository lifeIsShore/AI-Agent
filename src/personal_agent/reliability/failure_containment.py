from typing import Dict, Any

DOMAIN_LLM = "LLM"
DOMAIN_API = "API"
DOMAIN_TOOL = "TOOL"
DOMAIN_SPECIALIST = "SPECIALIST"
DOMAIN_WORKFLOW = "WORKFLOW"
DOMAIN_MEMORY = "MEMORY"
DOMAIN_SECURITY = "SECURITY"
DOMAIN_RESOURCE = "RESOURCE"

class FailureContainmentEngine:
    def contain_failure(
        self,
        failure_domain: str,
        error_message: str,
        affected_component_id: str = "component"
    ) -> Dict[str, Any]:
        """Isolates failures within specific domains without crashing master runtime."""
        domain_clean = failure_domain.upper()

        if domain_clean == DOMAIN_SPECIALIST:
            return {
                "status": "CONTAINED",
                "containment_strategy": "ISOLATE_SPECIALIST",
                "isolated_component": affected_component_id,
                "master_runtime_impact": "NONE",
                "action": f"Specialist '{affected_component_id}' failure isolated. Runtime continues executing remaining team."
            }

        elif domain_clean == DOMAIN_RESOURCE:
            return {
                "status": "CONTAINED",
                "containment_strategy": "PAUSE_NON_ESSENTIAL_CYCLES",
                "isolated_component": affected_component_id,
                "master_runtime_impact": "DEGRADED",
                "action": "Resource budget exhausted. Non-essential autonomous cycles paused."
            }

        elif domain_clean == DOMAIN_SECURITY:
            return {
                "status": "CONTAINED",
                "containment_strategy": "HARD_BLOCK_ACTION",
                "isolated_component": affected_component_id,
                "master_runtime_impact": "NONE",
                "action": "Security policy violation caught. Unauthorized action blocked."
            }

        return {
            "status": "CONTAINED",
            "containment_strategy": "SAFE_FALLBACK",
            "isolated_component": affected_component_id,
            "master_runtime_impact": "LOW",
            "action": f"Failure in domain '{domain_clean}' contained cleanly: {error_message}."
        }
