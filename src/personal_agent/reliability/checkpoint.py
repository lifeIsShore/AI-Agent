from typing import Dict, Any, List, Optional
from personal_agent.telemetry.store import TelemetryStore
from personal_agent.telemetry.tracer import (
    STEP_TOOL_EXECUTION_SUCCESS, STEP_MEMORY_UPDATED, STEP_TRACE_COMPLETED
)

class RecoveryCheckpointEngine:
    def __init__(self, telemetry_store: Optional[TelemetryStore] = None):
        self.store = telemetry_store or TelemetryStore()

    def get_incomplete_traces(self) -> List[Dict[str, Any]]:
        """Scans recorded telemetry traces for incomplete workflow traces (started but not completed)."""
        all_traces = self.store.load_all_traces()
        traces_by_id: Dict[str, List[Dict[str, Any]]] = {}

        for tr in all_traces:
            t_id = tr.get("trace_id")
            if t_id:
                if t_id not in traces_by_id:
                    traces_by_id[t_id] = []
                traces_by_id[t_id].append(tr)

        incomplete = []
        for t_id, steps in traces_by_id.items():
            step_names = [s.get("step") for s in steps if s.get("step")]
            if STEP_TRACE_COMPLETED not in step_names and len(step_names) > 0:
                incomplete.append({
                    "trace_id": t_id,
                    "steps": steps,
                    "last_step": step_names[-1],
                    "tool_executed": STEP_TOOL_EXECUTION_SUCCESS in step_names
                })

        return incomplete

    def evaluate_recovery_action(self, trace_id: str) -> Dict[str, Any]:
        """Determines the recovery action required for an incomplete trace.
        Ensures tools that succeeded before crash are NOT executed again (Zero Duplicate Execution).
        """
        all_traces = self.store.load_all_traces()
        trace_steps = [tr for tr in all_traces if tr.get("trace_id") == trace_id]
        step_names = [s.get("step") for s in trace_steps if s.get("step")]

        if STEP_TOOL_EXECUTION_SUCCESS in step_names:
            return {
                "trace_id": trace_id,
                "resume_step": STEP_MEMORY_UPDATED,
                "skip_tool_execution": True,
                "reason": "Tool execution already completed prior to crash. Resuming from Memory Update."
            }
        
        return {
            "trace_id": trace_id,
            "resume_step": step_names[-1] if step_names else "RETRY_FROM_START",
            "skip_tool_execution": False,
            "reason": "Process crashed prior to tool execution. Resuming proposal workflow."
        }
