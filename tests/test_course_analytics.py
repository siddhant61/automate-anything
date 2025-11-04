"""
Tests for course analytics module.
"""

import pytest
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session

from src.analysis import course_analytics
from src.models.tables import Course, Enrollment, User


@pytest.fixture
def sample_enrollments(test_db: Session):
    """Create sample enrollment data."""
    # Create courses
    course1 = Course(
        course_id="java2024",
        title="Java Course 2024",
        category="Java",
        language="de"
    )
    course2 = Course(
        course_id="python2024",
        title="Python Course 2024",
        category="Python",
        language="en"
    )
    test_db.add_all([course1, course2])
    test_db.commit()
    
    # Create users
    user1 = User(email="user1@test.com", username="user1")
    user2 = User(email="user2@test.com", username="user2")
    user3 = User(email="user3@test.com", username="user3")
    test_db.add_all([user1, user2, user3])
    test_db.commit()
    
    # Create enrollments
    enrollments = [
        Enrollment(
            user_id=user1.id,
            course_id="java2024",
            enrollment_date=datetime(2024, 3, 15),
            confirmation_of_participation=True,
            course_completed=True,
            items_visited_percentage=90.0,
            avg_session_duration=1200.0
        ),
        Enrollment(
            user_id=user2.id,
            course_id="java2024",
            enrollment_date=datetime(2024, 3, 20),
            record_of_achievement=True,
            course_completed=True,
            items_visited_percentage=85.0,
            avg_session_duration=1500.0
        ),
        Enrollment(
            user_id=user3.id,
            course_id="python2024",
            enrollment_date=datetime(2024, 4, 10),
            confirmation_of_participation=True,
            course_completed=False,
            items_visited_percentage=60.0,
            avg_session_duration=900.0
        ),
    ]
    test_db.add_all(enrollments)
    test_db.commit()
    
    return enrollments


def test_load_enrollment_data_from_db(test_db: Session, sample_enrollments):
    """Test loading enrollment data from database."""
    df = course_analytics.load_enrollment_data_from_db(test_db)
    
    assert not df.empty
    assert len(df) == 3
    assert 'enrollment_date' in df.columns
    assert 'category' in df.columns
    assert 'course_id' in df.columns


def test_load_enrollment_data_with_filters(test_db: Session, sample_enrollments):
    """Test loading enrollment data with filters."""
    # Filter by course_id
    df = course_analytics.load_enrollment_data_from_db(test_db, course_ids=["java2024"])
    assert len(df) == 2
    
    # Filter by year
    df = course_analytics.load_enrollment_data_from_db(test_db, years=[2024])
    assert len(df) == 3
    assert all(df['year'] == 2024)


def test_calculate_metrics(test_db: Session, sample_enrollments):
    """Test calculating metrics from enrollment data."""
    df = course_analytics.load_enrollment_data_from_db(test_db)
    metrics = course_analytics.calculate_metrics(df)
    
    assert 'certificates' in metrics
    assert 'average_session_length' in metrics
    assert 'items_visited_percentage' in metrics
    assert 'completion_rates' in metrics


def test_get_monthly_enrollments(test_db: Session, sample_enrollments):
    """Test getting monthly enrollment counts."""
    df = course_analytics.load_enrollment_data_from_db(test_db)
    monthly = course_analytics.get_monthly_enrollments(df)
    
    assert not monthly.empty
    assert 'Java' in monthly.columns or 'Python' in monthly.columns


def test_get_certificate_metrics(test_db: Session, sample_enrollments):
    """Test getting certificate metrics."""
    df = course_analytics.load_enrollment_data_from_db(test_db)
    cert_metrics = course_analytics.get_certificate_metrics(df)
    
    assert 'certificates' in cert_metrics
    assert len(cert_metrics['certificates']) > 0


def test_prepare_visualization_data(test_db: Session, sample_enrollments):
    """Test preparing visualization data."""
    data = course_analytics.prepare_visualization_data(test_db, years=[2024])
    
    assert 'enrollment_raw' in data
    assert 'enrollment_filtered' in data
    assert 'monthly_enrollments' in data
    assert 'metrics' in data
    assert 'certificates' in data


def test_filter_by_fixed_periods():
    """Test filtering data by fixed periods."""
    # Create sample data
    data = {
        'enrollment_date': pd.to_datetime([
            '2024-01-15', '2024-03-15', '2024-05-20', '2024-08-01'
        ]),
        'value': [1, 2, 3, 4]
    }
    df = pd.DataFrame(data)
    
    # Filter by fixed periods
    filtered = course_analytics.filter_by_fixed_periods(df, course_analytics.FIXED_PERIODS)
    
    # Should include dates in the 2024 period (2024-03-01 to 2024-06-30)
    assert len(filtered) == 2  # March and May entries


def test_calculate_metrics_empty_dataframe():
    """Test calculating metrics with empty dataframe."""
    # Create empty dataframe with required columns
    df = pd.DataFrame(columns=[
        'year', 'category', 'confirmation_of_participation', 'record_of_achievement',
        'course_completed', 'avg_session_duration', 'items_visited_percentage'
    ])
    metrics = course_analytics.calculate_metrics(df)
    
    # Should return empty metrics without errors
    assert isinstance(metrics, dict)
