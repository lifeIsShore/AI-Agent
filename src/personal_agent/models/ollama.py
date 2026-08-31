import json
import requests
from typing import Dict, Any, List, Optional
from personal_agent.config.settings import settings

class OllamaClient:
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.default_model

    def generate(self, prompt: str, system: Optional[str] = None, format: Optional[str] = None) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if system:
            payload["system"] = system
        if format:
            payload["format"] = format
            
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("response", "")

    def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        if tools:
            payload["tools"] = tools
            
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("message", {})
