import json
from typing import Dict, Any, List, Optional
from personal_agent.security.identity import IdentityProvider

class AgentAPIServer:
    def __init__(self, mode_provider=None, approval_queue=None, telemetry_store=None):
        self.mode_provider = mode_provider
        self.approval_queue = approval_queue
        self.telemetry_store = telemetry_store

    def handle_request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Routes HTTP-style REST API requests to corresponding agent control handlers."""
        method = method.upper()

        if method == "GET" and path == "/health":
            return self.get_health()
        elif method == "GET" and path == "/agent/status":
            return self.get_status()
        elif method == "POST" and path == "/agent/run":
            return self.run_agent(body or {})
        elif method == "GET" and path == "/proposals":
            return self.get_proposals()
        elif method == "POST" and path.startswith("/proposals/") and path.endswith("/approve"):
            pid = path.split("/")[2]
            return self.approve_proposal(pid)
        elif method == "POST" and path.startswith("/proposals/") and path.endswith("/reject"):
            pid = path.split("/")[2]
            return self.reject_proposal(pid)
        elif method == "GET" and path.startswith("/traces/"):
            tid = path.split("/")[2]
            return self.get_trace(tid)

        return {"status": 404, "error": f"Endpoint '{method} {path}' not found."}

    def get_health(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY",
            "components": {
                "scheduler": "HEALTHY",
                "event_bus": "HEALTHY",
                "policy_engine": "HEALTHY",
                "credential_broker": "HEALTHY",
                "model_router": "HEALTHY"
            }
        }

    def get_status(self) -> Dict[str, Any]:
        current_mode = self.mode_provider.get_mode() if self.mode_provider else "NORMAL"
        user_p = IdentityProvider.get_user_principal()
        return {
            "agent_status": "RUNNING",
            "runtime_mode": current_mode,
            "active_principal": user_p.principal_id,
            "policy_version": "2.0.0",
            "uptime_seconds": 12840.5
        }

    def run_agent(self, body: Dict[str, Any]) -> Dict[str, Any]:
        prompt = body.get("prompt", "")
        if not prompt:
            return {"status": 400, "error": "Missing 'prompt' parameter."}
        
        current_mode = self.mode_provider.get_mode() if self.mode_provider else "NORMAL"
        if current_mode == "EMERGENCY_STOP":
            return {"status": 403, "error": "Agent is in EMERGENCY_STOP mode. All requests are denied."}

        return {
            "status": 200,
            "workflow_id": f"wf_{prompt[:8]}",
            "message": f"Agent workflow launched for prompt: '{prompt}'"
        }

    def get_proposals(self) -> Dict[str, Any]:
        pending = self.approval_queue.list_pending() if self.approval_queue else []
        return {
            "count": len(pending),
            "pending_proposals": [p.to_dict() for p in pending]
        }

    def approve_proposal(self, proposal_id: str) -> Dict[str, Any]:
        if not self.approval_queue:
            return {"status": 500, "error": "Approval queue not initialized."}
        res = self.approval_queue.approve_proposal(proposal_id)
        return {"proposal_id": proposal_id, "action": "approved", "result": str(res)}

    def reject_proposal(self, proposal_id: str) -> Dict[str, Any]:
        if not self.approval_queue:
            return {"status": 500, "error": "Approval queue not initialized."}
        res = self.approval_queue.reject_proposal(proposal_id)
        return {"proposal_id": proposal_id, "action": "rejected", "result": str(res)}

    def get_trace(self, trace_id: str) -> Dict[str, Any]:
        return {
            "trace_id": trace_id,
            "status": "COMPLETED",
            "steps_count": 7
        }
