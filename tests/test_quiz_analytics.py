"""
Tests for quiz analytics module.
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from src.analysis import quiz_analytics
from src.models.tables import Course, QuizResult, User


@pytest.fixture
def sample_quiz_data(test_db: Session):
    """Create sample quiz data."""
    # Create courses
    courses = [
        Course(
            course_id="course1",
            title="Test Course 1",
            category="Programming"
        ),
        Course(
            course_id="course2",
            title="Test Course 2",
            category="Programming"
        ),
    ]
    test_db.add_all(courses)
    test_db.commit()
    
    # Create users
    users = [User(email=f"user{i}@test.com", username=f"user{i}") for i in range(5)]
    test_db.add_all(users)
    test_db.commit()
    
    # Create quiz results
    quiz_results = [
        QuizResult(
            user_id=users[0].id,
            course_id="course1",
            quiz_name="Quiz 1",
            quiz_type="graded",
            score=85,
            max_score=100,
            percentage=85.0,
            attempts=1,
            time_spent=600
        ),
        QuizResult(
            user_id=users[1].id,
            course_id="course1",
            quiz_name="Quiz 1",
            quiz_type="graded",
            score=65,
            max_score=100,
            percentage=65.0,
            attempts=2,
            time_spent=900
        ),
        QuizResult(
            user_id=users[2].id,
            course_id="course1",
            quiz_name="Quiz 2",
            quiz_type="ungraded",
            score=90,
            max_score=100,
            percentage=90.0,
            attempts=1,
            time_spent=450
        ),
        QuizResult(
            user_id=users[3].id,
            course_id="course2",
            quiz_name="Quiz 1",
            quiz_type="graded",
            score=50,
            max_score=100,
            percentage=50.0,
            attempts=3,
            time_spent=1200
        ),
    ]
    test_db.add_all(quiz_results)
    test_db.commit()
    
    return quiz_results


def test_load_quiz_data_from_db(test_db: Session, sample_quiz_data):
    """Test loading quiz data from database."""
    df = quiz_analytics.load_quiz_data_from_db(test_db)
    
    assert not df.empty
    assert len(df) == 4
    assert 'quiz_name' in df.columns
    assert 'score' in df.columns
    assert 'percentage' in df.columns


def test_load_quiz_data_with_filters(test_db: Session, sample_quiz_data):
    """Test loading quiz data with filters."""
    # Filter by course_id
    df = quiz_analytics.load_quiz_data_from_db(test_db, course_ids=["course1"])
    assert len(df) == 3
    
    # Filter by quiz_type
    df = quiz_analytics.load_quiz_data_from_db(test_db, quiz_type="graded")
    assert len(df) == 3
    assert all(df['quiz_type'] == 'graded')


def test_calculate_quiz_performance_metrics(test_db: Session, sample_quiz_data):
    """Test calculating quiz performance metrics."""
    df = quiz_analytics.load_quiz_data_from_db(test_db)
    metrics = quiz_analytics.calculate_quiz_performance_metrics(df)
    
    assert metrics['total_submissions'] == 4
    assert 'average_score' in metrics
    assert 'average_percentage' in metrics
    assert 'pass_rate' in metrics
    assert 'average_attempts' in metrics
    
    # Pass rate should be 75% (3 out of 4 scored >= 60%)
    # 85%, 65%, 90% pass (>=60%), 50% fails
    assert metrics['pass_rate'] == 75.0


def test_calculate_quiz_performance_metrics_empty():
    """Test calculating metrics with empty data."""
    import pandas as pd
    df = pd.DataFrame()
    metrics = quiz_analytics.calculate_quiz_performance_metrics(df)
    
    assert metrics['total_submissions'] == 0
    assert metrics['average_score'] == 0.0


def test_get_quiz_performance_by_course(test_db: Session, sample_quiz_data):
    """Test getting performance metrics by course."""
    df = quiz_analytics.load_quiz_data_from_db(test_db)
    performance = quiz_analytics.get_quiz_performance_by_course(df)
    
    assert not performance.empty
    assert 'course_id' in performance.columns
    assert 'submissions' in performance.columns
    assert 'avg_percentage' in performance.columns
    assert 'pass_rate' in performance.columns


def test_get_quiz_performance_by_type(test_db: Session, sample_quiz_data):
    """Test getting performance metrics by quiz type."""
    df = quiz_analytics.load_quiz_data_from_db(test_db)
    performance = quiz_analytics.get_quiz_performance_by_type(df)
    
    assert not performance.empty
    assert 'quiz_type' in performance.columns
    assert 'submissions' in performance.columns
    assert 'avg_percentage' in performance.columns


def test_compare_quiz_performance(test_db: Session, sample_quiz_data):
    """Test comparing quiz performance across courses."""
    comparison = quiz_analytics.compare_quiz_performance(
        test_db,
        course_ids=["course1", "course2"]
    )
    
    assert 'courses' in comparison
    assert 'comparison' in comparison
    assert len(comparison['courses']) == 2


def test_get_quiz_time_analysis(test_db: Session, sample_quiz_data):
    """Test quiz time analysis."""
    df = quiz_analytics.load_quiz_data_from_db(test_db)
    time_analysis = quiz_analytics.get_quiz_time_analysis(df)
    
    assert not time_analysis.empty
    assert 'quiz_type' in time_analysis.columns
    assert 'avg_time' in time_analysis.columns
    
    # Time should be converted to minutes
    assert all(time_analysis['avg_time'] < 100)  # Should be in minutes, not seconds


def test_get_quiz_time_analysis_no_time_data():
    """Test time analysis with no time_spent data."""
    import pandas as pd
    df = pd.DataFrame({
        'quiz_type': ['graded', 'ungraded'],
        'score': [80, 90]
    })
    
    time_analysis = quiz_analytics.get_quiz_time_analysis(df)
    assert time_analysis.empty
