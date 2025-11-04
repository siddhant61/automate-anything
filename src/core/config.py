"""
Configuration management using Pydantic Settings.

All configuration is loaded from environment variables or .env file.
This is the single source of truth for all application configuration.
"""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenHPI Platform Configuration
    openhpi_username: str = Field(default="", description="OpenHPI platform username")
    openhpi_password: str = Field(default="", description="OpenHPI platform password")
    openhpi_base_url: str = Field(default="https://open.hpi.de", description="OpenHPI base URL")
    
    # Helpdesk Configuration
    helpdesk_url: str = Field(default="https://helpdesk.openhpi.de", description="Helpdesk URL")
    helpdesk_username: str = Field(default="", description="Helpdesk username")
    helpdesk_password: str = Field(default="", description="Helpdesk password")
    
    # Email Configuration
    smtp_host: str = Field(default="smtp.gmail.com", description="SMTP server host")
    smtp_port: int = Field(default=587, description="SMTP server port")
    smtp_username: str = Field(default="", description="SMTP username")
    smtp_password: str = Field(default="", description="SMTP password")
    email_from: str = Field(default="", description="Default sender email address")
    email_to: str = Field(default="", description="Default recipient email address")
    
    # Telegram Configuration
    telegram_bot_token: str = Field(default="", description="Telegram bot token")
    telegram_chat_id: str = Field(default="", description="Telegram chat ID")
    
    # Google AI Configuration
    google_api_key: str = Field(default="", description="Google Generative AI API key")
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./openhpi_automation.db",
        description="Database connection URL"
    )
    
    # Data Storage Paths
    data_dir: Path = Field(default=Path("./data"), description="Directory for data files")
    reports_dir: Path = Field(default=Path("./reports"), description="Directory for reports")
    exports_dir: Path = Field(default=Path("./exports"), description="Directory for exports")
    
    # Application Settings
    env: str = Field(default="development", description="Environment (development/staging/production)")
    debug: bool = Field(default=True, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    api_workers: int = Field(default=4, description="Number of API workers")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.env.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.env.lower() == "development"


# Global settings instance
settings = Settings()
