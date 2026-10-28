from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    database_url: str = "sqlite:///./devpilot.db"
    api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    model_name: str = "llama2"
    docker_sandbox_image: str = "devpilot-sandbox:latest"
    approved_repos_paths: str = os.getcwd()
    max_execution_time: int = 300
    max_memory_mb: int = 512
    log_level: str = "INFO"
    deterministic_mode: bool = True
    
    class Config:
        env_file = ".env"
    
    def get_approved_paths(self) -> List[str]:
        paths = self.approved_repos_paths.split(';')
        return [p.strip() for p in paths if p.strip()]

settings = Settings()
