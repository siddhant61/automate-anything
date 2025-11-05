"""
Tests for courses API endpoints.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from datetime import datetime

from src.main import app
from src.models.tables import Course


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestCoursesEndpoints:
    """Test courses API endpoints."""

    def test_list_courses_empty(self, client):
        """Test listing courses with empty database."""
        response = client.get("/api/courses/")
        
        assert response.status_code == 200
        data = response.json()
        assert 'courses' in data
        assert isinstance(data['courses'], list)

    def test_list_courses_with_filters(self, client):
        """Test listing courses with filters."""
        response = client.get("/api/courses/?language=English&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert 'courses' in data

    def test_get_course_not_found(self, client):
        """Test getting non-existent course."""
        response = client.get("/api/courses/nonexistent-course-id")
        
        assert response.status_code == 404
        assert 'not found' in response.json()['detail'].lower()

    def test_get_course_stats_not_found(self, client):
        """Test getting stats for non-existent course."""
        response = client.get("/api/courses/nonexistent-course-id/stats")
        
        assert response.status_code == 404

    def test_list_courses_pagination(self, client):
        """Test listing courses with pagination."""
        response = client.get("/api/courses/?skip=0&limit=50")
        
        assert response.status_code == 200
        data = response.json()
        assert 'total' in data
        assert 'skip' in data
        assert 'limit' in data

    def test_list_courses_category_filter(self, client):
        """Test filtering courses by category."""
        response = client.get("/api/courses/?category=Programming")
        
        assert response.status_code == 200
        data = response.json()
        assert 'courses' in data


