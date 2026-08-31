from typing import List, Dict, Any, Optional
from personal_agent.models.ollama import OllamaClient

class ModelGateway:
    def __init__(self, provider: str = "ollama"):
        self.provider = provider
        if self.provider == "ollama":
            self.client = OllamaClient()
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def generate(self, prompt: str, system: Optional[str] = None, format: Optional[str] = None) -> str:
        return self.client.generate(prompt=prompt, system=system, format=format)

    def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        return self.client.chat(messages=messages, tools=tools)
