"""
Tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date

from src.main import app
from src.models.database import Base, SessionLocal, engine
from src.models.tables import Course, ScrapingJob


@pytest.fixture(scope="module")
def test_client():
    """Create a test client."""
    # Create test database
    Base.metadata.create_all(bind=engine)
    
    # Import tables to register models
    from src.models import tables  # noqa: F401
    
    client = TestClient(app)
    yield client
    
    # Cleanup is handled by database isolation


@pytest.fixture
def sample_courses():
    """Create sample courses in database."""
    db = SessionLocal()
    
    courses = [
        Course(
            course_id="test-java-2024",
            title="Test Java Course",
            description="Test course",
            category="Java",
            language="en"
        ),
        Course(
            course_id="test-python-2024",
            title="Test Python Course",
            description="Test course",
            category="Python",
            language="en"
        )
    ]
    
    for course in courses:
        db.add(course)
    db.commit()
    
    yield courses
    
    # Cleanup
    for course in courses:
        db.delete(course)
    db.commit()
    db.close()


def test_root_endpoint(test_client):
    """Test root endpoint."""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "OpenHPI Automation API"
    assert data["status"] == "operational"


def test_health_endpoint(test_client):
    """Test health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_courses_empty(test_client):
    """Test listing courses when database is empty."""
    response = test_client.get("/api/courses/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["courses"], list)


def test_list_courses_with_data(test_client, sample_courses):
    """Test listing courses with sample data."""
    response = test_client.get("/api/courses/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["count"] >= 2  # At least our sample courses


def test_get_course_by_id(test_client, sample_courses):
    """Test getting a specific course."""
    response = test_client.get("/api/courses/test-java-2024")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["course"]["course_id"] == "test-java-2024"
    assert data["course"]["title"] == "Test Java Course"


def test_get_nonexistent_course(test_client):
    """Test getting a course that doesn't exist."""
    response = test_client.get("/api/courses/nonexistent-course")
    assert response.status_code == 404


def test_list_categories(test_client, sample_courses):
    """Test listing course categories."""
    response = test_client.get("/api/courses/categories/list")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Java" in data["categories"] or "Python" in data["categories"]


def test_list_scraping_jobs(test_client):
    """Test listing scraping jobs."""
    response = test_client.get("/api/scraping/jobs")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["jobs"], list)
