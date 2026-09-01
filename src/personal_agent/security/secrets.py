import os
from typing import Dict, Any, Optional

class SecretStore:
    def __init__(self):
        # Ephemeral internal secret storage (isolated from LLM contexts)
        self._secrets: Dict[str, str] = {
            "google_client_id": os.getenv("GOOGLE_CLIENT_ID", "mock_google_client_id_secret"),
            "google_refresh_token": os.getenv("GOOGLE_REFRESH_TOKEN", "mock_google_refresh_token_secret"),
            "ollama_api_key": os.getenv("OLLAMA_API_KEY", "local_ollama_key")
        }

    def get_secret(self, secret_name: str) -> Optional[str]:
        """Retrieves a secret strictly for tool runtime execution."""
        return self._secrets.get(secret_name)
