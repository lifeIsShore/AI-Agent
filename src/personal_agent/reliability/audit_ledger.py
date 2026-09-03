import os
import json
import time
import uuid
import tempfile
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

@dataclass
class AuditRecord:
    audit_id: str
    decision: str
    action: str
    authorization_level: str
    execution_status: str
    verification_status: str
    outcome_type: str
    evidence: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditRecord":
        return cls(
            audit_id=data.get("audit_id", f"aud_{uuid.uuid4().hex[:8]}"),
            decision=data.get("decision", "unknown"),
            action=data.get("action", "unknown"),
            authorization_level=data.get("authorization_level", "LEVEL_0"),
            execution_status=data.get("execution_status", "UNKNOWN"),
            verification_status=data.get("verification_status", "UNKNOWN"),
            outcome_type=data.get("outcome_type", "UNKNOWN"),
            evidence=data.get("evidence", []),
            timestamp=data.get("timestamp", time.time())
        )

class AuditLedger:
    def __init__(self, storage_dir: Optional[str] = None, filename: str = "audit_ledger.json"):
        if storage_dir:
            self.storage_dir = os.path.abspath(storage_dir)
            self.filepath = os.path.join(self.storage_dir, filename)
            os.makedirs(self.storage_dir, exist_ok=True)
            self.records: List[AuditRecord] = self.load_audits()
        else:
            self.storage_dir = None
            self.filepath = None
            self.records: List[AuditRecord] = []

    def record_audit(
        self,
        decision: str,
        action: str,
        authorization_level: str,
        execution_status: str,
        verification_status: str,
        outcome_type: str,
        evidence: Optional[List[str]] = None
    ) -> AuditRecord:
        rec = AuditRecord(
            audit_id=f"aud_{uuid.uuid4().hex[:8]}",
            decision=decision,
            action=action,
            authorization_level=authorization_level,
            execution_status=execution_status,
            verification_status=verification_status,
            outcome_type=outcome_type,
            evidence=evidence or [],
            timestamp=time.time()
        )
        self.records.append(rec)
        if self.filepath:
            self.save_audits()
        return rec

    def save_audits(self) -> None:
        if not self.filepath or not self.storage_dir:
            return
        data = [r.to_dict() for r in self.records]
        temp_fd, temp_path = tempfile.mkstemp(dir=self.storage_dir, prefix="aud_tmp_", suffix=".json")
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, self.filepath)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            print(f"[AuditLedger ERROR] Failed to save audit ledger: {e}")

    def load_audits(self) -> List[AuditRecord]:
        if not self.filepath or not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return [AuditRecord.from_dict(d) for d in data]
        except Exception as e:
            print(f"[AuditLedger WARNING] Failed to load audits: {e}. Starting fresh.")
            return []
