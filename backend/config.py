import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    app_name: str = "Factify API"
    version: str = "1.0.0"
    debug: bool = False
    
    # API Keys
    openai_api_key: str = ""
    google_fact_check_api_key: str = ""
    anthropic_api_key: str = ""
    google_ai_api_key: str = ""
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    allowed_origins: List[str] = ["*"]
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # Database
    database_url: str = "sqlite:///./factify.db"
    
    # External APIs
    timeout_seconds: int = 30
    max_text_length: int = 5000
    min_text_length: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()