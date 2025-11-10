"""
Tests for configuration management.
"""

import os
import pytest
from src.core.config import Settings


def test_settings_default_values():
    """Test that Settings loads with default values."""
    settings = Settings()
    
    assert settings.env == "development"
    assert settings.debug is True
    assert settings.openhpi_base_url == "https://open.hpi.de"
    # database_url is now SecretStr, need to get the actual value
    db_url = settings.database_url.get_secret_value() if settings.database_url else ""
    assert db_url.startswith("sqlite:")


def test_settings_from_env(monkeypatch):
    """Test that Settings loads from environment variables."""
    monkeypatch.setenv("OPENHPI_USERNAME", "testuser")
    monkeypatch.setenv("OPENHPI_PASSWORD", "testpass")
    monkeypatch.setenv("ENV", "production")
    
    settings = Settings()
    
    assert settings.openhpi_username == "testuser"
    # openhpi_password is now SecretStr, need to get the actual value
    assert settings.openhpi_password.get_secret_value() == "testpass"
    assert settings.env == "production"


def test_settings_is_production():
    """Test environment detection methods."""
    settings = Settings(env="production")
    assert settings.is_production is True
    assert settings.is_development is False
    
    settings = Settings(env="development")
    assert settings.is_production is False
    assert settings.is_development is True


def test_settings_case_insensitive(monkeypatch):
    """Test that environment variables are case-insensitive."""
    monkeypatch.setenv("OPENHPI_USERNAME", "TestUser")
    settings = Settings()
    assert settings.openhpi_username == "TestUser"


def test_settings_no_credential_leak_in_repr(monkeypatch):
    """Test that sensitive credentials are not exposed in repr() or str()."""
    monkeypatch.setenv("OPENHPI_PASSWORD", "secret-password-123")
    monkeypatch.setenv("GOOGLE_API_KEY", "sk-1234567890abcdef")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot-token-secret")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:dbpass123@localhost/db")
    
    settings = Settings()
    
    # Test repr() doesn't expose secrets
    repr_str = repr(settings)
    assert "secret-password-123" not in repr_str
    assert "sk-1234567890abcdef" not in repr_str
    assert "bot-token-secret" not in repr_str
    assert "dbpass123" not in repr_str
    
    # Test that secrets are masked with ***
    assert "openhpi_password='***'" in repr_str
    assert "google_api_key='***'" in repr_str
    assert "telegram_bot_token='***'" in repr_str
    
    # Test str() doesn't expose secrets
    str_str = str(settings)
    assert "secret-password-123" not in str_str
    assert "sk-1234567890abcdef" not in str_str
    assert "bot-token-secret" not in str_str
    assert "dbpass123" not in str_str
    
    # Test that actual values are still accessible via get_secret_value()
    assert settings.openhpi_password.get_secret_value() == "secret-password-123"
    assert settings.google_api_key.get_secret_value() == "sk-1234567890abcdef"
    assert settings.telegram_bot_token.get_secret_value() == "bot-token-secret"


def test_settings_database_url_safe_display():
    """Test that database URL is safely displayed with password masked."""
    settings = Settings(database_url="postgresql://user:secret123@localhost/db")
    
    safe_url = settings.get_database_url_safe()
    
    # Password should be masked
    assert "secret123" not in safe_url
    assert "***" in safe_url
    assert "postgresql://user:***@localhost/db" == safe_url
    
    # But actual value should still be accessible
    assert settings.database_url.get_secret_value() == "postgresql://user:secret123@localhost/db"

