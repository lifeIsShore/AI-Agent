import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    default_model: str = os.getenv("DEFAULT_MODEL", "qwen2.5:1.5b")

    class Config:
        env_file = ".env"

settings = Settings()
