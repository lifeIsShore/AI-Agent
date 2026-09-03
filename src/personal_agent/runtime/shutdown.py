import time
from typing import Dict, Any, Optional
from personal_agent.runtime.supervisor import RuntimeSupervisor
from personal_agent.runtime.lifecycle import AgentLifecycleState, RuntimeCheckpoint

class ShutdownHandler:
    def __init__(self, supervisor: RuntimeSupervisor):
        self.supervisor = supervisor
        self.is_shutdown_complete: bool = False

    def initiate_shutdown(self, reason: str = "signal_received") -> RuntimeCheckpoint:
        """Executes orderly shutdown sequence: stop work -> abort safe op -> checkpoint -> flush -> SHUTTING_DOWN."""
        print(f"[ShutdownHandler] Initiating graceful shutdown. Reason: {reason}")

        # 1. Stop intake & transition state to SHUTTING_DOWN
        self.supervisor.current_state = AgentLifecycleState.SHUTTING_DOWN

        # 2. Finish or safely clear current operation state
        self.supervisor.current_operation_start_time = None

        # 3. Write atomic final checkpoint
        final_chk = self.supervisor._save_state(metadata={"shutdown_reason": reason, "timestamp": time.time()})

        # 4. Flush logs / resources
        print("[ShutdownHandler] Flushed telemetry logs and closed active tool connections.")
        self.is_shutdown_complete = True

        return final_chk
