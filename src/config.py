"""Configuration and constants for Karumi Toolkit"""

from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    
    # Browser Settings
    headless: bool = True
    browser_timeout: int = 30000  # milliseconds
    screenshot_on_failure: bool = True
    
    # Testing Settings
    max_retries: int = 3
    retry_delay: int = 2  # seconds
    test_timeout: int = 60  # seconds
    
    # Monitoring Settings
    log_level: str = "INFO"
    enable_sentry: bool = False
    sentry_dsn: Optional[str] = None
    
    # Dashboard Settings
    dashboard_port: int = 8501  # Streamlit default
    api_port: int = 8000  # FastAPI default
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
