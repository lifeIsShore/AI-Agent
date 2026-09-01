from typing import Dict, List, Optional
from personal_agent.scheduler.job import Job

class JobRegistry:
    def __init__(self):
        self.jobs: Dict[str, Job] = {}

    def register(self, job: Job):
        """Registers a scheduled Job."""
        self.jobs[job.job_id] = job

    def get_job(self, job_id: str) -> Optional[Job]:
        """Retrieves a job by its ID."""
        return self.jobs.get(job_id)

    def list_jobs(self) -> List[Job]:
        """Lists all registered jobs."""
        return list(self.jobs.values())

    def get_due_jobs(self) -> List[Job]:
        """Returns all jobs currently due for execution."""
        return [job for job in self.jobs.values() if job.is_due()]
