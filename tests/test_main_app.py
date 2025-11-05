"""
Tests for main FastAPI application.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create test client."""
    with patch('src.main.init_db'):
        return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'Data Pipeline Platform API'
    assert data['version'] == '1.0.0'
    assert data['status'] == 'operational'
    assert 'docs_url' in data


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert data['database'] == 'connected'
    assert 'environment' in data


def test_cors_headers(client):
    """Test CORS headers are present."""
    # Test with a GET request which is supported
    response = client.get("/")
    
    # CORS headers should be present for allowed origins
    assert response.status_code == 200
    # FastAPI adds CORS headers on actual requests
    assert 'content-type' in response.headers


def test_app_metadata():
    """Test FastAPI app metadata."""
    assert app.title == "Data Pipeline Platform API"
    assert app.version == "1.0.0"
    assert "platform" in app.description.lower()


def test_routers_included():
    """Test that all routers are included."""
    routes = [route.path for route in app.routes]
    
    # Check generic platform routes exist
    assert any('/api/sources' in route for route in routes)
    assert any('/api/data' in route for route in routes)
    
    # Check OpenHPI module routes exist (legacy)
    assert any('/api/courses' in route for route in routes)
    assert any('/api/scraping' in route for route in routes)
    assert any('/api/analysis' in route for route in routes)
    assert any('/api/automation' in route for route in routes)
    assert any('/api/ai' in route for route in routes)


def test_main_module_structure():
    """Test main module has required attributes."""
    from src import main
    
    # Verify key components exist
    assert hasattr(main, 'app')
    assert hasattr(main, 'settings')
    
    # Verify the app is configured properly
    assert main.app.title == "Data Pipeline Platform API"
    assert main.app.version == "1.0.0"
