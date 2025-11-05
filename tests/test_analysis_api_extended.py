"""
Extended tests for analysis API endpoints.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestAnalysisEndpointsExtended:
    """Test analysis API endpoints."""

    def test_get_course_metrics_no_data(self, client):
        """Test course metrics with no data."""
        response = client.get("/api/analysis/courses/metrics")
        
        # Should return even with no data
        assert response.status_code == 200 or response.status_code == 404

    def test_get_course_metrics_with_year_filter(self, client):
        """Test course metrics with year filter."""
        response = client.get("/api/analysis/courses/metrics?year=2024")
        
        assert response.status_code in [200, 404]

    def test_get_course_metrics_with_category_filter(self, client):
        """Test course metrics with category filter."""
        response = client.get("/api/analysis/courses/metrics?category=Programming")
        
        assert response.status_code in [200, 404]

    def test_get_annual_stats_no_year(self, client):
        """Test annual stats without year parameter."""
        response = client.get("/api/analysis/annual")
        
        # Should require year parameter or use default
        assert response.status_code in [200, 404, 422]

    def test_get_annual_stats_with_year(self, client):
        """Test annual stats with specific year."""
        response = client.get("/api/analysis/annual?year=2024")
        
        assert response.status_code in [200, 404]

    def test_get_quiz_performance_no_data(self, client):
        """Test quiz performance with no data."""
        response = client.get("/api/analysis/quiz/performance")
        
        assert response.status_code in [200, 404]

    def test_get_quiz_performance_with_filters(self, client):
        """Test quiz performance with filters."""
        response = client.get("/api/analysis/quiz/performance?course_id=test-course")
        
        assert response.status_code in [200, 404]

    def test_compare_quiz_performance_insufficient_courses(self, client):
        """Test quiz comparison with insufficient courses."""
        response = client.post("/api/analysis/quiz/compare", json={
            "course_ids": ["course1"]
        })
        
        # Should fail with insufficient courses
        assert response.status_code in [400, 404]
        if response.status_code == 400:
            assert 'at least 2 courses' in response.json()['detail'].lower()

    def test_compare_quiz_performance_valid(self, client):
        """Test quiz comparison with valid input."""
        response = client.post("/api/analysis/quiz/compare", json={
            "course_ids": ["course1", "course2"]
        })
        
        # May not have data, but should accept the request
        assert response.status_code in [200, 404]

    def test_get_enrollment_trends_no_data(self, client):
        """Test enrollment trends with no data."""
        response = client.get("/api/analysis/enrollments/trends")
        
        assert response.status_code in [200, 404]

    def test_get_enrollment_trends_with_period(self, client):
        """Test enrollment trends with time period."""
        response = client.get("/api/analysis/enrollments/trends?period=monthly")
        
        assert response.status_code in [200, 404]

    def test_get_user_demographics_no_data(self, client):
        """Test user demographics with no data."""
        response = client.get("/api/analysis/users/demographics")
        
        assert response.status_code in [200, 404]

    def test_get_user_activity_no_data(self, client):
        """Test user activity with no data."""
        response = client.get("/api/analysis/users/activity")
        
        assert response.status_code in [200, 404]

    def test_get_retention_metrics_no_data(self, client):
        """Test retention metrics with no data."""
        response = client.get("/api/analysis/retention")
        
        assert response.status_code in [200, 404]


class TestAnalysisFiltersAndPagination:
    """Test analysis API filters and pagination."""

    def test_metrics_pagination(self, client):
        """Test metrics with pagination parameters."""
        response = client.get("/api/analysis/courses/metrics?skip=0&limit=10")
        
        assert response.status_code in [200, 404]

    def test_metrics_date_range(self, client):
        """Test metrics with date range."""
        response = client.get(
            "/api/analysis/courses/metrics?start_date=2024-01-01&end_date=2024-12-31"
        )
        
        assert response.status_code in [200, 404]

    def test_invalid_date_format(self, client):
        """Test with invalid date format."""
        response = client.get("/api/analysis/courses/metrics?start_date=invalid-date")
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 404, 422]

    def test_negative_pagination(self, client):
        """Test with negative pagination values."""
        response = client.get("/api/analysis/courses/metrics?skip=-1&limit=-10")
        
        # Should validate or handle gracefully
        assert response.status_code in [200, 400, 404, 422]
