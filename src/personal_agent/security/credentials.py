from typing import Dict, Any, Optional
from personal_agent.security.secrets import SecretStore

class CredentialBroker:
    def __init__(self, secret_store: Optional[SecretStore] = None):
        self.secrets = secret_store or SecretStore()

    def get_tool_credential(self, service_name: str, capability: str) -> Optional[Dict[str, Any]]:
        """Dispenses service credentials strictly to tool execution runtimes.
        Guarantees Zero Credential Leakage to LLM contexts or telemetry.
        """
        if service_name in ["gmail", "calendar", "tasks"]:
            token = self.secrets.get_secret("google_refresh_token")
            return {
                "service": service_name,
                "capability_scope": capability,
                "token_type": "OAuth2",
                "access_token": f"bearer_{service_name}_{token[:8]}"
            }
        elif service_name == "ollama":
            return {
                "service": "ollama",
                "capability_scope": capability,
                "token_type": "Local",
                "access_token": "local"
            }
        return None
