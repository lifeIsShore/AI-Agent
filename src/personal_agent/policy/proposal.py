import uuid
import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List

# Action Proposal Lifecycle Status Constants
STATUS_PROPOSED = "PROPOSED"
STATUS_AUTO_APPROVED = "AUTO_APPROVED"
STATUS_PENDING_APPROVAL = "PENDING_APPROVAL"
STATUS_DENIED = "DENIED"
STATUS_APPROVED = "APPROVED"
STATUS_REJECTED = "REJECTED"
STATUS_EXECUTED = "EXECUTED"
STATUS_FAILED = "FAILED"
STATUS_EXPIRED = "EXPIRED"

@dataclass
class ActionProposal:
    action: str
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    confidence: float = 1.0
    risk_level: str = "LOW"             # LOW | MEDIUM | HIGH | CRITICAL
    required_permission: str = "READ_ONLY" # READ_ONLY | ANALYZE | PROPOSE | MODIFY
    status: str = STATUS_PROPOSED       # PROPOSED | AUTO_APPROVED | PENDING_APPROVAL | DENIED | APPROVED | REJECTED | EXECUTED | FAILED | EXPIRED
    proposal_id: str = field(default_factory=lambda: f"prop_{uuid.uuid4().hex[:8]}")
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: Optional[str] = None    # ISO timestamp string (e.g. default TTL: 30 minutes)
    why_proposed: List[str] = field(default_factory=list) # Explainability chain breakdown
    target_checksum: Optional[str] = None # Hash/snapshot of target state for stale proposal validation
    parameters_hash: Optional[str] = None # Deterministic SHA256 hash binding for parameter tamper-protection
    audit_metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.parameters_hash:
            self.parameters_hash = self.compute_parameters_hash()

    def compute_parameters_hash(self) -> str:
        """Calculates deterministic SHA256 parameter hash binding."""
        raw = f"{self.action}:{self.target}:{json.dumps(self.parameters, sort_keys=True)}"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]

    def verify_parameters_integrity(self) -> bool:
        """Verifies current action parameters match the original parameters_hash."""
        return self.compute_parameters_hash() == self.parameters_hash

    def is_expired(self) -> bool:
        """Returns True if the proposal has exceeded its expiration timestamp."""
        if not self.expires_at:
            return False
        try:
            exp_dt = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
            now_dt = datetime.now(timezone.utc)
            return now_dt >= exp_dt
        except ValueError:
            return False

    def format_explainable_card(self) -> str:
        """Renders rich pre-execution explainability card presentation."""
        why_str = "\n".join([f"  ├─ {w}" for w in self.why_proposed]) if self.why_proposed else f"  └─ {self.reason or 'Automated recommendation'}"
        return (
            f"┌─────────────────────────────────────────────┐\n"
            f"│ ACTION PROPOSAL: {self.action:<25} │\n"
            f"├─────────────────────────────────────────────┤\n"
            f"│ Target:     {self.target:<31} │\n"
            f"│ Risk Level: {self.risk_level:<31} │\n"
            f"│ Parameters: {json.dumps(self.parameters)[:31]:<31} │\n"
            f"│ WHY:                                        │\n"
            f"{why_str}\n"
            f"└─────────────────────────────────────────────┘"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "action": self.action,
            "target": self.target,
            "parameters": self.parameters,
            "reason": self.reason,
            "confidence": self.confidence,
            "risk_level": self.risk_level,
            "required_permission": self.required_permission,
            "status": self.status,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "why_proposed": self.why_proposed,
            "target_checksum": self.target_checksum,
            "parameters_hash": self.parameters_hash or self.compute_parameters_hash(),
            "audit_metadata": self.audit_metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActionProposal':
        return cls(
            proposal_id=data.get("proposal_id", f"prop_{uuid.uuid4().hex[:8]}"),
            action=data.get("action", ""),
            target=data.get("target", ""),
            parameters=data.get("parameters", {}),
            reason=data.get("reason", ""),
            confidence=data.get("confidence", 1.0),
            risk_level=data.get("risk_level", "LOW"),
            required_permission=data.get("required_permission", "READ_ONLY"),
            status=data.get("status", STATUS_PROPOSED),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            expires_at=data.get("expires_at"),
            why_proposed=data.get("why_proposed", []),
            target_checksum=data.get("target_checksum"),
            parameters_hash=data.get("parameters_hash"),
            audit_metadata=data.get("audit_metadata", {})
        )
