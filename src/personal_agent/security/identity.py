from typing import Optional
from personal_agent.security.principal import (
    Principal, PRINCIPAL_USER, PRINCIPAL_SCHEDULER, PRINCIPAL_SYSTEM, PRINCIPAL_AGENT
)

class IdentityProvider:
    @staticmethod
    def get_user_principal(user_id: str = "user_ahmet") -> Principal:
        return Principal(
            principal_id=user_id,
            principal_type=PRINCIPAL_USER,
            assigned_capabilities=["*"]
        )

    @staticmethod
    def get_scheduler_principal(job_id: str = "daemon_scheduler") -> Principal:
        return Principal(
            principal_id=job_id,
            principal_type=PRINCIPAL_SCHEDULER,
            assigned_capabilities=["gmail.read", "calendar.read", "tasks.read"]
        )

    @staticmethod
    def get_agent_principal(agent_id: str = "personal_agent_runtime") -> Principal:
        return Principal(
            principal_id=agent_id,
            principal_type=PRINCIPAL_AGENT,
            assigned_capabilities=["gmail.read", "calendar.read", "tasks.read", "system.read"]
        )
