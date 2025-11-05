"""
Tests for scraping API endpoints.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from datetime import datetime

from src.main import app
from src.models.tables import ScrapingJob


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Create mock database session."""
    db = Mock()
    db.query.return_value.filter_by.return_value.first.return_value = None
    db.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
    return db


class TestScrapingEndpoints:
    """Test scraping API endpoints."""

    @patch('src.api.scraping.scrape_courses')
    @patch('src.api.scraping.get_db')
    def test_scrape_courses_success(self, mock_get_db, mock_scrape, client, mock_db):
        """Test successful course scraping."""
        mock_get_db.return_value = mock_db
        mock_scrape.return_value = {
            'status': 'success',
            'courses_scraped': 10,
            'courses_saved': 10,
            'job_id': 1
        }
        
        response = client.post("/api/scraping/courses")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert '10 courses' in data['message']

    @patch('src.api.scraping.scrape_courses')
    @patch('src.api.scraping.get_db')
    def test_scrape_courses_scraping_error(self, mock_get_db, mock_scrape, client, mock_db):
        """Test scraping error handling."""
        from src.services.scraping_service import ScrapingError
        
        mock_get_db.return_value = mock_db
        mock_scrape.side_effect = ScrapingError("Failed to scrape")
        
        response = client.post("/api/scraping/courses")
        
        assert response.status_code == 500
        assert 'Scraping error' in response.json()['detail']

    @patch('src.api.scraping.scrape_courses')
    @patch('src.api.scraping.get_db')
    def test_scrape_courses_unexpected_error(self, mock_get_db, mock_scrape, client, mock_db):
        """Test unexpected error handling."""
        mock_get_db.return_value = mock_db
        mock_scrape.side_effect = Exception("Unexpected error")
        
        response = client.post("/api/scraping/courses")
        
        assert response.status_code == 500
        assert 'Unexpected error' in response.json()['detail']

    def test_list_scraping_jobs(self, client):
        """Test listing scraping jobs."""
        # Use actual database with test data
        response = client.get("/api/scraping/jobs")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'count' in data
        assert 'jobs' in data
        # With a fresh test DB, should have 0 jobs
        assert isinstance(data['jobs'], list)

    @patch('src.api.scraping.get_db')
    def test_list_scraping_jobs_with_limit(self, mock_get_db, client):
        """Test listing jobs with custom limit."""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        response = client.get("/api/scraping/jobs?limit=5")
        
        assert response.status_code == 200
        # Verify limit was passed (can't check actual call without more mocking)

    def test_get_scraping_job_not_found(self, client):
        """Test getting non-existent job."""
        response = client.get("/api/scraping/jobs/999")
        
        assert response.status_code == 404
        assert 'not found' in response.json()['detail'].lower()
