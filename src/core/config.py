"""
Configuration management using Pydantic Settings.

All configuration is loaded from environment variables or .env file.
This is the single source of truth for all application configuration.
"""

from pathlib import Path
from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenHPI Platform Configuration
    openhpi_username: str = Field(default="", description="OpenHPI platform username")
    openhpi_password: SecretStr = Field(default="", description="OpenHPI platform password")
    openhpi_base_url: str = Field(default="https://open.hpi.de", description="OpenHPI base URL")
    
    # Helpdesk Configuration
    helpdesk_url: str = Field(default="https://helpdesk.openhpi.de", description="Helpdesk URL")
    helpdesk_username: str = Field(default="", description="Helpdesk username")
    helpdesk_password: SecretStr = Field(default="", description="Helpdesk password")
    
    # Email Configuration
    smtp_host: str = Field(default="smtp.gmail.com", description="SMTP server host")
    smtp_port: int = Field(default=587, description="SMTP server port")
    smtp_username: str = Field(default="", description="SMTP username")
    smtp_password: SecretStr = Field(default="", description="SMTP password")
    email_from: str = Field(default="", description="Default sender email address")
    email_to: str = Field(default="", description="Default recipient email address")
    
    # Telegram Configuration
    telegram_bot_token: SecretStr = Field(default="", description="Telegram bot token")
    telegram_chat_id: str = Field(default="", description="Telegram chat ID")
    
    # Google AI Configuration
    google_api_key: SecretStr = Field(default="", description="Google Generative AI API key")
    
    # Database Configuration
    database_url: SecretStr = Field(
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
    
    def get_database_url_safe(self) -> str:
        """
        Get database URL with credentials masked for safe display.
        
        Returns:
            Database URL with password masked (e.g., postgresql://user:***@host/db)
        """
        db_url = self.database_url.get_secret_value() if self.database_url else ""
        if not db_url:
            return "Not configured"
        
        # Mask password in URL if present
        if "://" in db_url and "@" in db_url:
            # Split into scheme and rest
            scheme, rest = db_url.split("://", 1)
            # Check if there's authentication
            if "@" in rest:
                auth, host_db = rest.split("@", 1)
                if ":" in auth:
                    username, _ = auth.split(":", 1)
                    return f"{scheme}://{username}:***@{host_db}"
        return db_url
    
    def __repr__(self) -> str:
        """
        Custom repr that masks sensitive fields.
        
        Returns:
            String representation with sensitive values masked
        """
        return (
            f"Settings("
            f"openhpi_username='{self.openhpi_username}', "
            f"openhpi_password='***', "
            f"openhpi_base_url='{self.openhpi_base_url}', "
            f"helpdesk_url='{self.helpdesk_url}', "
            f"helpdesk_username='{self.helpdesk_username}', "
            f"helpdesk_password='***', "
            f"smtp_host='{self.smtp_host}', "
            f"smtp_port={self.smtp_port}, "
            f"smtp_username='{self.smtp_username}', "
            f"smtp_password='***', "
            f"email_from='{self.email_from}', "
            f"email_to='{self.email_to}', "
            f"telegram_bot_token='***', "
            f"telegram_chat_id='{self.telegram_chat_id}', "
            f"google_api_key='***', "
            f"database_url='{self.get_database_url_safe()}', "
            f"data_dir={self.data_dir!r}, "
            f"reports_dir={self.reports_dir!r}, "
            f"exports_dir={self.exports_dir!r}, "
            f"env='{self.env}', "
            f"debug={self.debug}, "
            f"log_level='{self.log_level}', "
            f"api_host='{self.api_host}', "
            f"api_port={self.api_port}, "
            f"api_workers={self.api_workers}"
            f")"
        )


# Global settings instance
settings = Settings()
