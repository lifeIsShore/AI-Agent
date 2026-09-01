import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from personal_agent.scheduler.registry import JobRegistry
from personal_agent.scheduler.job import Job
from personal_agent.state.manager import StateManager

class AgentScheduler:
    def __init__(self, registry: Optional[JobRegistry] = None, state_manager: Optional[StateManager] = None):
        self.registry = registry or JobRegistry()
        self.state_manager = state_manager or StateManager()
        self.execution_history: List[Dict[str, Any]] = []

    def register_job(self, job: Job):
        """Registers a Job in the scheduler."""
        self.registry.register(job)

    def run_pending_jobs(self) -> List[Dict[str, Any]]:
        """Checks registered jobs and executes any that are due."""
        due_jobs = self.registry.get_due_jobs()
        results = []

        for job in due_jobs:
            start_time = datetime.now(timezone.utc).isoformat()
            try:
                out = job.handler()
                job.mark_executed()
                entry = {
                    "job_id": job.job_id,
                    "name": job.name,
                    "status": "SUCCESS",
                    "output": out,
                    "executed_at": start_time,
                    "next_run": job.next_run
                }
            except Exception as e:
                job.mark_executed()
                entry = {
                    "job_id": job.job_id,
                    "name": job.name,
                    "status": "FAILED",
                    "error": str(e),
                    "executed_at": start_time,
                    "next_run": job.next_run
                }

            results.append(entry)
            self.execution_history.append(entry)

        # Save runtime state to disk
        self._save_runtime_state()
        return results

    def _save_runtime_state(self):
        """Helper to sync current scheduler job states to disk."""
        runtime_data = {
            "last_tick": datetime.now(timezone.utc).isoformat(),
            "jobs": [
                {
                    "job_id": j.job_id,
                    "name": j.name,
                    "interval_minutes": j.interval_minutes,
                    "enabled": j.enabled,
                    "last_run": j.last_run,
                    "next_run": j.next_run
                }
                for j in self.registry.list_jobs()
            ],
            "execution_history": self.execution_history[-20:]
        }
        self.state_manager.save_runtime_state(runtime_data)

    def run_daemon_tick(self) -> List[Dict[str, Any]]:
        """Executes a single daemon evaluation tick."""
        return self.run_pending_jobs()
