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
    assert settings.database_url.startswith("sqlite:")


def test_settings_from_env(monkeypatch):
    """Test that Settings loads from environment variables."""
    monkeypatch.setenv("OPENHPI_USERNAME", "testuser")
    monkeypatch.setenv("OPENHPI_PASSWORD", "testpass")
    monkeypatch.setenv("ENV", "production")
    
    settings = Settings()
    
    assert settings.openhpi_username == "testuser"
    assert settings.openhpi_password == "testpass"
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
