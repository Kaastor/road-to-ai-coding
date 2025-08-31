from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application settings
    app_name: str = "ML Model Registry"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Database settings
    database_url: str = "sqlite:///./models.db"
    
    # Storage settings
    artifact_storage_path: Path = Path("./artifacts")
    max_artifact_size_mb: int = 100
    
    # API settings
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    
    # Security settings
    cors_origins: list[str] = ["*"]
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def __post_init__(self):
        """Post-initialization setup."""
        # Ensure artifact storage directory exists
        self.artifact_storage_path.mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()