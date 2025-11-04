"""
Course analytics module - Ported from course_analytics.py.

This module provides data analysis functions for course performance metrics,
reading from the production database instead of CSV files.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from src.models.database import get_db
from src.models.tables import Course, CourseStats, Enrollment


# Define the fixed periods for analysis
FIXED_PERIODS = {
    '2021': ('2021-02-01', '2021-06-30'),
    '2022': ('2022-03-01', '2022-06-30'),
    '2023': ('2023-01-01', '2023-06-30'),
    '2024': ('2024-03-01', '2024-06-30')
}


def load_enrollment_data_from_db(
    db: Session, 
    course_ids: Optional[List[str]] = None,
    years: Optional[List[int]] = None
) -> pd.DataFrame:
    """
    Load and prepare enrollment data from the database.
    
    Args:
        db: Database session
        course_ids: Optional list of course IDs to filter
        years: Optional list of years to filter
        
    Returns:
        DataFrame with enrollment data
    """
    # Build query
    query = db.query(
        Enrollment,
        Course.title,
        Course.category,
        Course.language
    ).join(Course, Enrollment.course_id == Course.course_id)
    
    # Apply filters
    if course_ids:
        query = query.filter(Enrollment.course_id.in_(course_ids))
    
    # Execute query
    results = query.all()
    
    # Convert to DataFrame
    data = []
    for enrollment, course_title, category, language in results:
        data.append({
            'enrollment_date': enrollment.enrollment_date,
            'course_id': enrollment.course_id,
            'course_title': course_title,
            'category': category,
            'language': language,
            'confirmation_of_participation': enrollment.confirmation_of_participation,
            'record_of_achievement': enrollment.record_of_achievement,
            'course_completed': enrollment.course_completed,
            'items_visited_percentage': enrollment.items_visited_percentage,
            'avg_session_duration': enrollment.avg_session_duration,
        })
    
    df = pd.DataFrame(data)
    
    if df.empty:
        return df
    
    # Prepare data
    df['enrollment_date'] = pd.to_datetime(df['enrollment_date'], errors='coerce')
    df['enrollment_month'] = df['enrollment_date'].dt.to_period('M')
    
    # Extract year from enrollment_date
    df['year'] = df['enrollment_date'].dt.year
    
    # Filter by years if specified
    if years:
        df = df[df['year'].isin(years)]
    
    return df


def load_course_stats_from_db(
    db: Session,
    course_ids: Optional[List[str]] = None,
    years: Optional[List[int]] = None
) -> pd.DataFrame:
    """
    Load course statistics from the database.
    
    Args:
        db: Database session
        course_ids: Optional list of course IDs to filter
        years: Optional list of years to filter
        
    Returns:
        DataFrame with course statistics
    """
    query = db.query(
        CourseStats,
        Course.title,
        Course.category
    ).join(Course, CourseStats.course_id == Course.course_id)
    
    if course_ids:
        query = query.filter(CourseStats.course_id.in_(course_ids))
    if years:
        query = query.filter(CourseStats.year.in_(years))
    
    results = query.all()
    
    data = []
    for stats, course_title, category in results:
        data.append({
            'course_id': stats.course_id,
            'course_title': course_title,
            'category': category,
            'year': stats.year,
            'total_enrollments': stats.total_enrollments,
            'active_users': stats.active_users,
            'certificates_issued': stats.certificates_issued,
            'completion_rate': stats.completion_rate,
            'average_progress': stats.average_progress,
            'average_session_duration': stats.average_session_duration,
            'items_visited_percentage': stats.items_visited_percentage,
            'graded_quiz_performance': stats.graded_quiz_performance,
            'ungraded_quiz_performance': stats.ungraded_quiz_performance,
            'recorded_at': stats.recorded_at,
        })
    
    return pd.DataFrame(data)


def calculate_metrics(df: pd.DataFrame, group_by: List[str] = ['year', 'category']) -> Dict[str, pd.Series]:
    """
    Calculate key performance metrics from enrollment data.
    
    Args:
        df: DataFrame with enrollment data
        group_by: Columns to group by
        
    Returns:
        Dictionary of metric name to Series
    """
    metrics = {}
    
    # Certificates
    cert_filter = (df['confirmation_of_participation'] == True) | (df['record_of_achievement'] == True)
    metrics['certificates'] = df[cert_filter].groupby(group_by).size()
    
    # Average session length
    metrics['average_session_length'] = df.groupby(group_by)['avg_session_duration'].mean()
    
    # Items visited percentage
    metrics['items_visited_percentage'] = df.groupby(group_by)['items_visited_percentage'].mean()
    
    # Completion rates
    metrics['completion_rates'] = df.groupby(group_by)['course_completed'].apply(
        lambda x: (x == True).sum() / len(x) if len(x) > 0 else 0
    )
    
    return metrics


def filter_by_fixed_periods(df: pd.DataFrame, fixed_periods: Dict[str, Tuple[str, str]]) -> pd.DataFrame:
    """
    Filter data within fixed time periods.
    
    Args:
        df: DataFrame with enrollment_date column
        fixed_periods: Dictionary mapping year to (start_date, end_date) tuple
        
    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df
    
    filtered_data = pd.DataFrame()
    for year, (start_date, end_date) in fixed_periods.items():
        period_data = df[
            (df['enrollment_date'] >= start_date) & 
            (df['enrollment_date'] <= end_date)
        ]
        filtered_data = pd.concat([filtered_data, period_data])
    
    return filtered_data


def calculate_drop_out_rates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate drop-out rates based on session activity.
    
    Drop-out condition: sessions < 2 AND total_session_duration < 600
    
    Args:
        df: DataFrame with enrollment data
        
    Returns:
        DataFrame with drop-out rates by year, category, and month
    """
    # Note: Original implementation requires 'sessions' and 'total_session_duration' columns
    # These need to be added to the Enrollment model or calculated separately
    # For now, returning empty DataFrame as placeholder
    return pd.DataFrame()


def get_monthly_enrollments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get monthly enrollment counts grouped by year and category.
    
    Args:
        df: DataFrame with enrollment data
        
    Returns:
        DataFrame with monthly enrollment counts
    """
    if df.empty:
        return df
    
    monthly = df.groupby(
        ['year', 'enrollment_month', 'category']
    ).size().unstack(fill_value=0)
    
    return monthly


def get_certificate_metrics(df: pd.DataFrame) -> Dict[str, pd.Series]:
    """
    Calculate certificate-related metrics.
    
    Args:
        df: DataFrame with enrollment data
        
    Returns:
        Dictionary of certificate metrics
    """
    metrics = {}
    
    # Certificates by year and category
    cert_filter = (df['confirmation_of_participation'] == True) | (df['record_of_achievement'] == True)
    metrics['certificates'] = df[cert_filter].groupby(['year', 'category']).size()
    
    return metrics


def prepare_visualization_data(
    db: Session,
    years: Optional[List[int]] = None,
    categories: Optional[List[str]] = None
) -> Dict[str, pd.DataFrame]:
    """
    Prepare all data needed for visualizations.
    
    Args:
        db: Database session
        years: Optional list of years to include
        categories: Optional list of categories to include (e.g., ['Java', 'Python'])
        
    Returns:
        Dictionary mapping data type to DataFrame
    """
    # Load enrollment data
    enrollment_df = load_enrollment_data_from_db(db, years=years)
    
    if not enrollment_df.empty and categories:
        enrollment_df = enrollment_df[enrollment_df['category'].isin(categories)]
    
    # Filter by fixed periods
    filtered_df = filter_by_fixed_periods(enrollment_df, FIXED_PERIODS)
    
    # Prepare data packages
    data = {
        'enrollment_raw': enrollment_df,
        'enrollment_filtered': filtered_df,
        'monthly_enrollments': get_monthly_enrollments(filtered_df),
        'metrics': calculate_metrics(filtered_df),
        'certificates': get_certificate_metrics(filtered_df),
    }
    
    return data
