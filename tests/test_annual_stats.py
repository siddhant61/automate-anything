"""
Tests for annual statistics module.
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from src.analysis import annual_stats
from src.models.tables import Course, Enrollment, User


@pytest.fixture
def sample_annual_data(test_db: Session):
    """Create sample annual data for 2023."""
    # Create courses
    courses = [
        Course(
            course_id="java2023",
            title="Java Course 2023",
            category="Java",
            language="de"
        ),
        Course(
            course_id="python2023",
            title="Python Course 2023",
            category="Python",
            language="en"
        ),
    ]
    test_db.add_all(courses)
    test_db.commit()
    
    # Create users
    users = [User(email=f"user{i}@test.com", username=f"user{i}") for i in range(5)]
    test_db.add_all(users)
    test_db.commit()
    
    # Create enrollments for 2023
    enrollments = [
        Enrollment(
            user_id=users[0].id,
            course_id="java2023",
            enrollment_date=datetime(2023, 3, 15),
            confirmation_of_participation=True,
            course_completed=True,
            items_visited_percentage=90.0,
            avg_session_duration=1200.0
        ),
        Enrollment(
            user_id=users[1].id,
            course_id="java2023",
            enrollment_date=datetime(2023, 4, 20),
            record_of_achievement=True,
            course_completed=True,
            items_visited_percentage=85.0,
            avg_session_duration=1500.0
        ),
        Enrollment(
            user_id=users[2].id,
            course_id="python2023",
            enrollment_date=datetime(2023, 5, 10),
            confirmation_of_participation=True,
            course_completed=False,
            items_visited_percentage=60.0,
            avg_session_duration=900.0
        ),
        Enrollment(
            user_id=users[3].id,
            course_id="python2023",
            enrollment_date=datetime(2023, 6, 5),
            record_of_achievement=True,
            course_completed=True,
            items_visited_percentage=95.0,
            avg_session_duration=1800.0
        ),
    ]
    test_db.add_all(enrollments)
    test_db.commit()
    
    return enrollments


def test_load_annual_data(test_db: Session, sample_annual_data):
    """Test loading annual data for a specific year."""
    df = annual_stats.load_annual_data(test_db, 2023)
    
    assert not df.empty
    assert len(df) == 4
    assert all(df['enrollment_date'].dt.year == 2023)
    assert 'course_language' in df.columns


def test_load_annual_data_no_data(test_db: Session):
    """Test loading annual data when no data exists."""
    df = annual_stats.load_annual_data(test_db, 2020)
    
    assert df.empty


def test_calculate_annual_metrics(test_db: Session, sample_annual_data):
    """Test calculating annual metrics."""
    df = annual_stats.load_annual_data(test_db, 2023)
    metrics = annual_stats.calculate_annual_metrics(df)
    
    assert metrics['total_enrollments'] == 4
    assert metrics['net_enrollments'] == 4
    assert metrics['german_enrollments'] == 2
    assert metrics['english_enrollments'] == 2
    assert metrics['total_certificates'] == 4
    assert metrics['overall_completion_rate'] == 75.0  # 3 out of 4 completed


def test_calculate_annual_metrics_empty():
    """Test calculating metrics with empty data."""
    import pandas as pd
    df = pd.DataFrame()
    metrics = annual_stats.calculate_annual_metrics(df)
    
    assert metrics['total_enrollments'] == 0
    assert metrics['overall_completion_rate'] == 0.0


def test_get_course_enrollments(test_db: Session, sample_annual_data):
    """Test getting enrollment counts by course."""
    df = annual_stats.load_annual_data(test_db, 2023)
    enrollments = annual_stats.get_course_enrollments(df)
    
    assert 'all' in enrollments
    assert 'german' in enrollments
    assert 'english' in enrollments
    
    assert len(enrollments['all']) == 2
    assert len(enrollments['german']) == 1
    assert len(enrollments['english']) == 1


def test_get_course_certificates(test_db: Session, sample_annual_data):
    """Test getting certificate counts by course."""
    df = annual_stats.load_annual_data(test_db, 2023)
    certificates = annual_stats.get_course_certificates(df)
    
    assert 'all' in certificates
    assert 'german' in certificates
    assert 'english' in certificates
    
    # All 4 enrollments have certificates
    assert len(certificates['all']) == 2


def test_get_course_completion_rates(test_db: Session, sample_annual_data):
    """Test calculating completion rates by course."""
    df = annual_stats.load_annual_data(test_db, 2023)
    completion_rates = annual_stats.get_course_completion_rates(df)
    
    assert 'all' in completion_rates
    assert 'german' in completion_rates
    assert 'english' in completion_rates
    
    # Check structure
    assert 'course_code' in completion_rates['all'].columns
    assert 'rate' in completion_rates['all'].columns


def test_generate_annual_report(test_db: Session, sample_annual_data):
    """Test generating complete annual report."""
    report = annual_stats.generate_annual_report(test_db, 2023)
    
    assert report['year'] == 2023
    assert 'metrics' in report
    assert 'enrollments' in report
    assert 'certificates' in report
    assert 'completion_rates' in report
    
    # Check nested structure
    assert 'all' in report['enrollments']
    assert 'german' in report['enrollments']
    assert 'english' in report['enrollments']
