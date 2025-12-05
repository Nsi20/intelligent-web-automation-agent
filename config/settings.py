"""Configuration management using Pydantic settings."""
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # LLM Configuration
    groq_api_key: str = Field(..., description="Groq API key for LLM")
    
    # Email Configuration
    email_enabled: bool = Field(default=False, description="Enable email notifications")
    smtp_host: str = Field(default="smtp.gmail.com", description="SMTP server host")
    smtp_port: int = Field(default=587, description="SMTP server port")
    smtp_user: Optional[str] = Field(default=None, description="SMTP username")
    smtp_password: Optional[str] = Field(default=None, description="SMTP password")
    email_from: Optional[str] = Field(default=None, description="From email address")
    email_to: Optional[str] = Field(default=None, description="To email address")
    
    # Browser Configuration
    browser_headless: bool = Field(default=True, description="Run browser in headless mode")
    browser_timeout: int = Field(default=30000, description="Browser timeout in milliseconds")
    screenshot_on_error: bool = Field(default=True, description="Take screenshot on errors")
    
    # Job Board Configuration
    job_search_keywords: str = Field(
        default="python developer,software engineer",
        description="Comma-separated job search keywords"
    )
    job_location: str = Field(default="remote", description="Job location")
    job_max_results: int = Field(default=20, description="Maximum job results to fetch")
    
    # Storage
    data_dir: Path = Field(default=Path("./data"), description="Data directory")
    logs_dir: Path = Field(default=Path("./logs"), description="Logs directory")
    
    # Application Settings
    log_level: str = Field(default="INFO", description="Logging level")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def keywords_list(self) -> list[str]:
        """Get job search keywords as a list."""
        return [k.strip() for k in self.job_search_keywords.split(",")]


# Global settings instance
settings = Settings()
