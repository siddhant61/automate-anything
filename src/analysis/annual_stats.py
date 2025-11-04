"""
Annual statistics module - Ported from annual_stats.Rmd.

This module provides annual report generation functionality,
translating R (ggplot2/dplyr) logic to Python (pandas/plotly).
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.models.tables import Course, Enrollment


def load_annual_data(
    db: Session,
    year: int
) -> pd.DataFrame:
    """
    Load enrollment data for a specific year.
    
    Args:
        db: Database session
        year: Year to load data for
        
    Returns:
        DataFrame with enrollment data for the specified year
    """
    # Query enrollments joined with course data
    query = db.query(
        Enrollment,
        Course.title,
        Course.category,
        Course.language,
        Course.course_id.label('course_code')
    ).join(Course, Enrollment.course_id == Course.course_id)
    
    results = query.all()
    
    # Convert to DataFrame
    data = []
    for enrollment, title, category, language, course_code in results:
        # Skip if no enrollment date
        if not enrollment.enrollment_date:
            continue
            
        data.append({
            'user_pseudo_id': enrollment.user_id,
            'course_code': course_code,
            'course_title': title,
            'category': category,
            'language': language,
            'enrollment_date': enrollment.enrollment_date,
            'confirmation_of_participation': enrollment.confirmation_of_participation,
            'record_of_achievement': enrollment.record_of_achievement,
            'course_completed': enrollment.course_completed,
            'items_visited_percentage': enrollment.items_visited_percentage,
            'avg_session_duration': enrollment.avg_session_duration,
        })
    
    df = pd.DataFrame(data)
    
    if df.empty:
        return df
    
    # Convert enrollment_date to datetime
    df['enrollment_date'] = pd.to_datetime(df['enrollment_date'], errors='coerce')
    
    # Filter for the specified year
    df = df[df['enrollment_date'].dt.year == year]
    
    # Add course_language column (same as language)
    df['course_language'] = df['language']
    
    return df


def calculate_annual_metrics(df: pd.DataFrame) -> Dict[str, any]:
    """
    Calculate annual metrics from enrollment data.
    
    Args:
        df: DataFrame with enrollment data
        
    Returns:
        Dictionary of metrics
    """
    if df.empty:
        return {
            'total_enrollments': 0,
            'net_enrollments': 0,
            'german_enrollments': 0,
            'english_enrollments': 0,
            'total_certificates': 0,
            'german_certificates': 0,
            'english_certificates': 0,
            'overall_completion_rate': 0.0,
            'german_completion_rate': 0.0,
            'english_completion_rate': 0.0,
        }
    
    # Total and net enrollments
    total_enrollments = len(df)
    net_enrollments = len(df)
    
    # Split by language
    df_de = df[df['course_language'] == 'de']
    df_en = df[df['course_language'] == 'en']
    
    # Language-specific enrollments
    german_enrollments = len(df_de)
    english_enrollments = len(df_en)
    
    # Certificates (ROA or COP)
    cert_filter = (df['confirmation_of_participation'] == True) | (df['record_of_achievement'] == True)
    total_certificates = df[cert_filter]['user_pseudo_id'].count()
    
    cert_filter_de = (df_de['confirmation_of_participation'] == True) | (df_de['record_of_achievement'] == True)
    german_certificates = df_de[cert_filter_de]['user_pseudo_id'].count()
    
    cert_filter_en = (df_en['confirmation_of_participation'] == True) | (df_en['record_of_achievement'] == True)
    english_certificates = df_en[cert_filter_en]['user_pseudo_id'].count()
    
    # Completion rates
    overall_completion_rate = (df['course_completed'].sum() / len(df) * 100) if len(df) > 0 else 0.0
    german_completion_rate = (df_de['course_completed'].sum() / len(df_de) * 100) if len(df_de) > 0 else 0.0
    english_completion_rate = (df_en['course_completed'].sum() / len(df_en) * 100) if len(df_en) > 0 else 0.0
    
    return {
        'total_enrollments': total_enrollments,
        'net_enrollments': net_enrollments,
        'german_enrollments': german_enrollments,
        'english_enrollments': english_enrollments,
        'total_certificates': total_certificates,
        'german_certificates': german_certificates,
        'english_certificates': english_certificates,
        'overall_completion_rate': round(overall_completion_rate, 2),
        'german_completion_rate': round(german_completion_rate, 2),
        'english_completion_rate': round(english_completion_rate, 2),
    }


def get_course_enrollments(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Get enrollment counts by course, split by language.
    
    Args:
        df: DataFrame with enrollment data
        
    Returns:
        Dictionary with 'all', 'german', and 'english' DataFrames
    """
    if df.empty:
        return {
            'all': pd.DataFrame(columns=['course_code', 'enrollments']),
            'german': pd.DataFrame(columns=['course_code', 'enrollments']),
            'english': pd.DataFrame(columns=['course_code', 'enrollments']),
        }
    
    # All courses
    courses_all = df.groupby('course_code').size().reset_index(name='enrollments')
    courses_all = courses_all.sort_values('enrollments', ascending=True)
    
    # German courses
    df_de = df[df['course_language'] == 'de']
    courses_de = df_de.groupby('course_code').size().reset_index(name='enrollments')
    courses_de = courses_de.sort_values('enrollments', ascending=True)
    
    # English courses
    df_en = df[df['course_language'] == 'en']
    courses_en = df_en.groupby('course_code').size().reset_index(name='enrollments')
    courses_en = courses_en.sort_values('enrollments', ascending=True)
    
    return {
        'all': courses_all,
        'german': courses_de,
        'english': courses_en,
    }


def get_course_certificates(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Get certificate counts by course, split by language.
    
    Args:
        df: DataFrame with enrollment data
        
    Returns:
        Dictionary with 'all', 'german', and 'english' DataFrames
    """
    if df.empty:
        return {
            'all': pd.DataFrame(columns=['course_code', 'certificates']),
            'german': pd.DataFrame(columns=['course_code', 'certificates']),
            'english': pd.DataFrame(columns=['course_code', 'certificates']),
        }
    
    # Filter for certificates (ROA or COP)
    cert_filter = (df['confirmation_of_participation'] == True) | (df['record_of_achievement'] == True)
    df_cert = df[cert_filter]
    
    # All courses
    courses_all = df_cert.groupby('course_code').size().reset_index(name='certificates')
    courses_all = courses_all.sort_values('certificates', ascending=True)
    
    # German courses
    df_de = df_cert[df_cert['course_language'] == 'de']
    courses_de = df_de.groupby('course_code').size().reset_index(name='certificates')
    courses_de = courses_de.sort_values('certificates', ascending=True)
    
    # English courses
    df_en = df_cert[df_cert['course_language'] == 'en']
    courses_en = df_en.groupby('course_code').size().reset_index(name='certificates')
    courses_en = courses_en.sort_values('certificates', ascending=True)
    
    return {
        'all': courses_all,
        'german': courses_de,
        'english': courses_en,
    }


def get_course_completion_rates(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Calculate completion rates by course, split by language.
    
    Args:
        df: DataFrame with enrollment data
        
    Returns:
        Dictionary with 'all', 'german', and 'english' DataFrames
    """
    if df.empty:
        return {
            'all': pd.DataFrame(columns=['course_code', 'enrollments', 'completions', 'rate']),
            'german': pd.DataFrame(columns=['course_code', 'enrollments', 'completions', 'rate']),
            'english': pd.DataFrame(columns=['course_code', 'enrollments', 'completions', 'rate']),
        }
    
    def calculate_rates(df_subset):
        # Total enrollments by course
        enrollments = df_subset.groupby('course_code').size().reset_index(name='enrollments')
        
        # Completions by course
        df_completed = df_subset[df_subset['course_completed'] == True]
        completions = df_completed.groupby('course_code').size().reset_index(name='completions')
        
        # Merge and calculate rate
        result = enrollments.merge(completions, on='course_code', how='left')
        result['completions'] = result['completions'].fillna(0)
        result['rate'] = (result['completions'] / result['enrollments'] * 100).round(2)
        result = result.sort_values('rate', ascending=True)
        
        return result
    
    # All courses
    courses_all = calculate_rates(df)
    
    # German courses
    df_de = df[df['course_language'] == 'de']
    courses_de = calculate_rates(df_de) if not df_de.empty else pd.DataFrame(columns=['course_code', 'enrollments', 'completions', 'rate'])
    
    # English courses
    df_en = df[df['course_language'] == 'en']
    courses_en = calculate_rates(df_en) if not df_en.empty else pd.DataFrame(columns=['course_code', 'enrollments', 'completions', 'rate'])
    
    return {
        'all': courses_all,
        'german': courses_de,
        'english': courses_en,
    }


def generate_annual_report(db: Session, year: int) -> Dict[str, any]:
    """
    Generate complete annual report for a given year.
    
    Args:
        db: Database session
        year: Year to generate report for
        
    Returns:
        Dictionary containing all annual statistics and data
    """
    # Load data
    df = load_annual_data(db, year)
    
    # Calculate metrics
    metrics = calculate_annual_metrics(df)
    
    # Get enrollment data
    enrollments = get_course_enrollments(df)
    
    # Get certificate data
    certificates = get_course_certificates(df)
    
    # Get completion rates
    completion_rates = get_course_completion_rates(df)
    
    return {
        'year': year,
        'metrics': metrics,
        'enrollments': {
            'all': enrollments['all'].to_dict('records'),
            'german': enrollments['german'].to_dict('records'),
            'english': enrollments['english'].to_dict('records'),
        },
        'certificates': {
            'all': certificates['all'].to_dict('records'),
            'german': certificates['german'].to_dict('records'),
            'english': certificates['english'].to_dict('records'),
        },
        'completion_rates': {
            'all': completion_rates['all'].to_dict('records'),
            'german': completion_rates['german'].to_dict('records'),
            'english': completion_rates['english'].to_dict('records'),
        }
    }
