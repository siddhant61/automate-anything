"""
Edge case tests for courses API to improve coverage.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestCoursesEndpointsEdgeCases:
    """Test courses API edge cases."""

    @patch('src.api.courses.get_db')
    def test_list_courses_with_all_filters(self, mock_get_db, client):
        """Test listing courses with all filters."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query
        
        response = client.get(
            "/api/courses/?category=Java&language=de&status=active&skip=10&limit=20"
        )
        
        assert response.status_code == 200

    @patch('src.api.courses.get_db')
    def test_get_course_by_id_not_found(self, mock_get_db, client):
        """Test getting non-existent course."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        response = client.get("/api/courses/nonexistent-course")
        
        assert response.status_code == 404

    @patch('src.api.courses.get_db')
    def test_get_course_stats_not_found(self, mock_get_db, client):
        """Test getting stats for non-existent course."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        response = client.get("/api/courses/nonexistent-course/stats")
        
        assert response.status_code == 404

    @patch('src.api.courses.get_db')
    def test_get_course_enrollments_not_found(self, mock_get_db, client):
        """Test getting enrollments for non-existent course."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        response = client.get("/api/courses/nonexistent-course/enrollments")
        
        assert response.status_code == 404

    @patch('src.api.courses.get_db')
    def test_get_course_analytics_not_found(self, mock_get_db, client):
        """Test getting analytics for non-existent course."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        response = client.get("/api/courses/nonexistent-course/analytics")
        
        assert response.status_code == 404

    @patch('src.api.courses.get_db')
    def test_list_courses_with_invalid_pagination(self, mock_get_db, client):
        """Test listing courses with invalid pagination."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query
        
        # Negative values should be handled by FastAPI validation or the endpoint
        response = client.get("/api/courses/?skip=-1&limit=-10")
        
        # Should either validate or handle gracefully
        assert response.status_code in [200, 422]

    @patch('src.api.courses.get_db')
    def test_list_courses_large_limit(self, mock_get_db, client):
        """Test listing courses with very large limit."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query
        
        response = client.get("/api/courses/?limit=10000")
        
        # FastAPI may validate and return 422, or endpoint may accept it
        assert response.status_code in [200, 422]

    @patch('src.api.courses.get_db')
    def test_get_course_with_database_error(self, mock_get_db, client):
        """Test getting course with database error."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.side_effect = Exception("Database connection failed")
        mock_db.query.return_value = mock_query
        
        response = client.get("/api/courses/test-course")
        
        # Should return error (may be 404 or 500 depending on error handling)
        assert response.status_code in [404, 500]

    @patch('src.api.courses.get_db')
    def test_list_courses_empty_filters(self, mock_get_db, client):
        """Test listing courses with empty filter values."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query
        
        response = client.get("/api/courses/?category=&language=")
        
        assert response.status_code == 200
