"""
Tests for analysis API endpoints.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.main import app
from src.models.tables import Course, Enrollment, User, QuizResult


client = TestClient(app)


@pytest.fixture
def sample_data(test_db: Session):
    """Create sample data for analysis."""
    # Create courses
    courses = [
        Course(course_id="test_course1", title="Test Course 1", category="Java", language="de"),
        Course(course_id="test_course2", title="Test Course 2", category="Python", language="en"),
    ]
    test_db.add_all(courses)
    test_db.commit()
    
    # Create users
    users = [User(email=f"user{i}@test.com", username=f"user{i}") for i in range(3)]
    test_db.add_all(users)
    test_db.commit()
    
    # Create enrollments
    enrollments = [
        Enrollment(
            user_id=users[0].id,
            course_id="test_course1",
            enrollment_date=datetime(2024, 3, 15),
            confirmation_of_participation=True,
            course_completed=True,
            items_visited_percentage=90.0,
            avg_session_duration=1200.0
        ),
        Enrollment(
            user_id=users[1].id,
            course_id="test_course2",
            enrollment_date=datetime(2024, 4, 10),
            record_of_achievement=True,
            course_completed=False,
            items_visited_percentage=60.0,
            avg_session_duration=900.0
        ),
    ]
    test_db.add_all(enrollments)
    test_db.commit()
    
    # Create quiz results
    quiz_results = [
        QuizResult(
            user_id=users[0].id,
            course_id="test_course1",
            quiz_name="Quiz 1",
            quiz_type="graded",
            score=85,
            max_score=100,
            percentage=85.0,
            attempts=1,
            time_spent=600
        ),
    ]
    test_db.add_all(quiz_results)
    test_db.commit()


@pytest.mark.skip(reason="SQLite threading issue with FastAPI TestClient")
def test_get_course_metrics(sample_data):
    """Test course metrics endpoint."""
    response = client.get("/api/analysis/course_metrics")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'monthly_enrollments' in data
    assert 'metrics' in data


@pytest.mark.skip(reason="SQLite threading issue with FastAPI TestClient")
def test_get_course_metrics_with_filters(sample_data):
    """Test course metrics with filters."""
    response = client.get("/api/analysis/course_metrics?years=2024&categories=Java")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True


@pytest.mark.skip(reason="SQLite threading issue with FastAPI TestClient")
def test_get_annual_stats(sample_data):
    """Test annual stats endpoint."""
    response = client.get("/api/analysis/annual_stats/2024")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'report' in data
    assert data['report']['year'] == 2024


@pytest.mark.skip(reason="SQLite threading issue with FastAPI TestClient")
def test_get_annual_stats_no_data():
    """Test annual stats for year with no data."""
    response = client.get("/api/analysis/annual_stats/2020")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True


@pytest.mark.skip(reason="SQLite threading issue with FastAPI TestClient")
def test_get_quiz_performance(sample_data):
    """Test quiz performance endpoint."""
    response = client.get("/api/analysis/quiz_performance")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'overall_metrics' in data
    assert 'by_course' in data
    assert 'by_type' in data


@pytest.mark.skip(reason="SQLite threading issue with FastAPI TestClient")
def test_get_quiz_performance_with_filters(sample_data):
    """Test quiz performance with filters."""
    response = client.get("/api/analysis/quiz_performance?course_ids=test_course1&quiz_type=graded")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True


@pytest.mark.skip(reason="SQLite threading issue with FastAPI TestClient")
def test_compare_quiz_performance(sample_data):
    """Test quiz comparison endpoint."""
    response = client.get("/api/analysis/quiz_comparison?course_ids=test_course1&course_ids=test_course2")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'comparison' in data


def test_compare_quiz_performance_insufficient_courses():
    """Test quiz comparison with insufficient courses."""
    response = client.get("/api/analysis/quiz_comparison?course_ids=test_course1")
    
    assert response.status_code == 400


@pytest.mark.skip(reason="SQLite threading issue with FastAPI TestClient")
def test_get_enrollment_trends(sample_data):
    """Test enrollment trends endpoint."""
    response = client.get("/api/analysis/enrollment_trends")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'monthly_enrollments' in data


@pytest.mark.skip(reason="SQLite threading issue with FastAPI TestClient")
def test_get_enrollment_trends_with_filters(sample_data):
    """Test enrollment trends with filters."""
    response = client.get("/api/analysis/enrollment_trends?years=2024&categories=Java")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
