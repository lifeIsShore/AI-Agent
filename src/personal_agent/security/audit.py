import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from personal_agent.policy.proposal import ActionProposal
from personal_agent.policy.capabilities import resolve_capability

class AuditLogger:
    def __init__(self, log_dir: str = "data/logs", log_filename: str = "audit.jsonl"):
        self.log_dir = log_dir
        self.log_file = os.path.join(self.log_dir, log_filename)
        os.makedirs(self.log_dir, exist_ok=True)

    def log_proposal(
        self,
        proposal: ActionProposal,
        policy_decision: str,
        user_approved: bool,
        execution_status: str,
        execution_result: Optional[Any] = None,
        latency_sec: float = 0.0,
        principal_id: str = "user_ahmet",
        credential_scope: str = "OAuth2"
    ) -> Dict[str, Any]:
        """Appends a structured, 15-field flight audit entry to audit.jsonl log file."""
        capability = resolve_capability(proposal.action) or proposal.action
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "proposal_id": proposal.proposal_id,
            "principal_id": principal_id,
            "action": proposal.action,
            "capability": capability,
            "target": proposal.target,
            "parameters": proposal.parameters,
            "parameters_hash": proposal.parameters_hash or proposal.compute_parameters_hash(),
            "reason": proposal.reason,
            "confidence": proposal.confidence,
            "risk_level": proposal.risk_level,
            "required_permission": proposal.required_permission,
            "policy_decision": policy_decision,
            "user_approved": user_approved,
            "credential_scope": credential_scope,
            "execution_status": execution_status,
            "execution_result": str(execution_result) if execution_result is not None else None,
            "latency_sec": round(latency_sec, 4)
        }

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[AuditLogger] Error writing audit log: {e}")

        return entry

    def get_recent_logs(
        self,
        limit: int = 20,
        action_filter: Optional[str] = None,
        risk_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Reads recent structured audit log entries from audit.jsonl."""
        if not os.path.exists(self.log_file):
            return []

        entries = []
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line_str = line.strip()
                    if line_str:
                        try:
                            record = json.loads(line_str)
                            if action_filter and record.get("action") != action_filter:
                                continue
                            if risk_filter and record.get("risk_level") != risk_filter:
                                continue
                            entries.append(record)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"[AuditLogger] Error reading audit log: {e}")

        return entries[-limit:]

    def clear_logs(self):
        """Clears the audit log file."""
        if os.path.exists(self.log_file):
            try:
                os.remove(self.log_file)
            except Exception as e:
                print(f"[AuditLogger] Error clearing log file: {e}")
