"""
Tests for database models and operations.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.database import Base
from src.models.tables import (
    Course, CourseStats, User, Enrollment, 
    QuizResult, HelpdeskTicket, ScrapingJob
)


@pytest.fixture
def db_session():
    """Create a test database session."""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Import tables to register models
    from src.models import tables  # noqa: F401
    
    yield session
    
    session.close()


def test_create_course(db_session):
    """Test creating a course."""
    course = Course(
        course_id="test-course-2024",
        title="Test Course",
        description="A test course",
        url="https://open.hpi.de/courses/test-course-2024",
        language="en",
        category="Testing"
    )
    
    db_session.add(course)
    db_session.commit()
    
    # Retrieve and verify
    retrieved = db_session.query(Course).filter_by(course_id="test-course-2024").first()
    assert retrieved is not None
    assert retrieved.title == "Test Course"
    assert retrieved.category == "Testing"


def test_create_user(db_session):
    """Test creating a user."""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User"
    )
    
    db_session.add(user)
    db_session.commit()
    
    retrieved = db_session.query(User).filter_by(email="test@example.com").first()
    assert retrieved is not None
    assert retrieved.username == "testuser"


def test_create_enrollment(db_session):
    """Test creating an enrollment with relationships."""
    # Create course
    course = Course(
        course_id="java-2024",
        title="Java Course",
        category="Java"
    )
    db_session.add(course)
    
    # Create user
    user = User(
        email="student@example.com",
        username="student"
    )
    db_session.add(user)
    db_session.commit()
    
    # Create enrollment
    enrollment = Enrollment(
        user_id=user.id,
        course_id=course.course_id,
        status="enrolled"
    )
    db_session.add(enrollment)
    db_session.commit()
    
    # Verify relationships
    retrieved = db_session.query(Enrollment).first()
    assert retrieved.user.email == "student@example.com"
    assert retrieved.course.title == "Java Course"


def test_create_course_stats(db_session):
    """Test creating course statistics."""
    # Create course first
    course = Course(
        course_id="python-2024",
        title="Python Course"
    )
    db_session.add(course)
    db_session.commit()
    
    # Create stats
    stats = CourseStats(
        course_id="python-2024",
        total_enrollments=100,
        active_users=75,
        completion_rate=0.65,
        year=2024
    )
    db_session.add(stats)
    db_session.commit()
    
    retrieved = db_session.query(CourseStats).first()
    assert retrieved.total_enrollments == 100
    assert retrieved.course.title == "Python Course"


def test_create_scraping_job(db_session):
    """Test creating a scraping job."""
    job = ScrapingJob(
        job_type="course_data",
        status="completed",
        records_processed=50,
        job_metadata={"source": "test", "version": "1.0"}
    )
    db_session.add(job)
    db_session.commit()
    
    retrieved = db_session.query(ScrapingJob).first()
    assert retrieved.job_type == "course_data"
    assert retrieved.status == "completed"
    assert retrieved.job_metadata["source"] == "test"
