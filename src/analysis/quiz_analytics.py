"""
Quiz analytics module - Ported from quiz_analysis.py and quiz_comparison.py.

This module provides analysis functions for quiz performance data.
"""

import pandas as pd
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.models.tables import Course, QuizResult, User


def load_quiz_data_from_db(
    db: Session,
    course_ids: Optional[List[str]] = None,
    quiz_type: Optional[str] = None
) -> pd.DataFrame:
    """
    Load quiz result data from the database.
    
    Args:
        db: Database session
        course_ids: Optional list of course IDs to filter
        quiz_type: Optional quiz type filter ('graded', 'ungraded', 'survey')
        
    Returns:
        DataFrame with quiz results
    """
    query = db.query(
        QuizResult,
        Course.title,
        Course.category,
        User.email
    ).join(Course, QuizResult.course_id == Course.course_id)\
     .join(User, QuizResult.user_id == User.id)
    
    if course_ids:
        query = query.filter(QuizResult.course_id.in_(course_ids))
    if quiz_type:
        query = query.filter(QuizResult.quiz_type == quiz_type)
    
    results = query.all()
    
    data = []
    for quiz, course_title, category, email in results:
        data.append({
            'quiz_id': quiz.id,
            'user_email': email,
            'course_id': quiz.course_id,
            'course_title': course_title,
            'category': category,
            'quiz_name': quiz.quiz_name,
            'quiz_type': quiz.quiz_type,
            'score': quiz.score,
            'max_score': quiz.max_score,
            'percentage': quiz.percentage,
            'attempts': quiz.attempts,
            'submitted_at': quiz.submitted_at,
            'time_spent': quiz.time_spent,
        })
    
    return pd.DataFrame(data)


def calculate_quiz_performance_metrics(df: pd.DataFrame) -> Dict[str, any]:
    """
    Calculate quiz performance metrics.
    
    Args:
        df: DataFrame with quiz results
        
    Returns:
        Dictionary of performance metrics
    """
    if df.empty:
        return {
            'total_submissions': 0,
            'average_score': 0.0,
            'average_percentage': 0.0,
            'median_percentage': 0.0,
            'pass_rate': 0.0,
            'average_attempts': 0.0,
        }
    
    # Calculate metrics
    total_submissions = len(df)
    average_score = df['score'].mean() if 'score' in df.columns else 0.0
    average_percentage = df['percentage'].mean() if 'percentage' in df.columns else 0.0
    median_percentage = df['percentage'].median() if 'percentage' in df.columns else 0.0
    
    # Pass rate (assuming 60% is passing)
    pass_threshold = 60.0
    pass_rate = (df['percentage'] >= pass_threshold).sum() / len(df) * 100 if 'percentage' in df.columns else 0.0
    
    # Average attempts
    average_attempts = df['attempts'].mean() if 'attempts' in df.columns else 0.0
    
    return {
        'total_submissions': total_submissions,
        'average_score': round(average_score, 2),
        'average_percentage': round(average_percentage, 2),
        'median_percentage': round(median_percentage, 2),
        'pass_rate': round(pass_rate, 2),
        'average_attempts': round(average_attempts, 2),
    }


def get_quiz_performance_by_course(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate quiz performance metrics grouped by course.
    
    Args:
        df: DataFrame with quiz results
        
    Returns:
        DataFrame with performance metrics by course
    """
    if df.empty:
        return pd.DataFrame(columns=['course_id', 'course_title', 'submissions', 'avg_percentage', 'pass_rate'])
    
    # Group by course
    grouped = df.groupby(['course_id', 'course_title']).agg({
        'quiz_id': 'count',
        'percentage': ['mean', 'median'],
    }).reset_index()
    
    # Flatten column names
    grouped.columns = ['course_id', 'course_title', 'submissions', 'avg_percentage', 'median_percentage']
    
    # Calculate pass rate per course
    pass_threshold = 60.0
    pass_rates = df[df['percentage'] >= pass_threshold].groupby('course_id').size()
    total_per_course = df.groupby('course_id').size()
    grouped['pass_rate'] = grouped['course_id'].map(lambda x: (pass_rates.get(x, 0) / total_per_course.get(x, 1) * 100) if total_per_course.get(x, 0) > 0 else 0.0)
    
    # Round values
    grouped['avg_percentage'] = grouped['avg_percentage'].round(2)
    grouped['median_percentage'] = grouped['median_percentage'].round(2)
    grouped['pass_rate'] = grouped['pass_rate'].round(2)
    
    return grouped.sort_values('avg_percentage', ascending=False)


def get_quiz_performance_by_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate quiz performance metrics grouped by quiz type.
    
    Args:
        df: DataFrame with quiz results
        
    Returns:
        DataFrame with performance metrics by quiz type
    """
    if df.empty:
        return pd.DataFrame(columns=['quiz_type', 'submissions', 'avg_percentage', 'pass_rate'])
    
    # Group by quiz type
    grouped = df.groupby('quiz_type').agg({
        'quiz_id': 'count',
        'percentage': ['mean', 'median'],
    }).reset_index()
    
    # Flatten column names
    grouped.columns = ['quiz_type', 'submissions', 'avg_percentage', 'median_percentage']
    
    # Calculate pass rate per type
    pass_threshold = 60.0
    pass_rates = df[df['percentage'] >= pass_threshold].groupby('quiz_type').size()
    total_per_type = df.groupby('quiz_type').size()
    grouped['pass_rate'] = grouped['quiz_type'].map(lambda x: (pass_rates.get(x, 0) / total_per_type.get(x, 1) * 100) if total_per_type.get(x, 0) > 0 else 0.0)
    
    # Round values
    grouped['avg_percentage'] = grouped['avg_percentage'].round(2)
    grouped['median_percentage'] = grouped['median_percentage'].round(2)
    grouped['pass_rate'] = grouped['pass_rate'].round(2)
    
    return grouped


def compare_quiz_performance(
    db: Session,
    course_ids: List[str]
) -> Dict[str, any]:
    """
    Compare quiz performance across multiple courses.
    
    Args:
        db: Database session
        course_ids: List of course IDs to compare
        
    Returns:
        Dictionary with comparison data
    """
    # Load data for all courses
    df = load_quiz_data_from_db(db, course_ids=course_ids)
    
    if df.empty:
        return {
            'courses': [],
            'comparison': pd.DataFrame().to_dict('records')
        }
    
    # Get performance by course
    performance = get_quiz_performance_by_course(df)
    
    # Get additional metrics per course
    comparison_data = []
    for course_id in course_ids:
        course_df = df[df['course_id'] == course_id]
        if not course_df.empty:
            metrics = calculate_quiz_performance_metrics(course_df)
            metrics['course_id'] = course_id
            metrics['course_title'] = course_df['course_title'].iloc[0]
            comparison_data.append(metrics)
    
    return {
        'courses': course_ids,
        'comparison': comparison_data
    }


def get_quiz_time_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze time spent on quizzes.
    
    Args:
        df: DataFrame with quiz results
        
    Returns:
        DataFrame with time analysis
    """
    if df.empty or 'time_spent' not in df.columns:
        return pd.DataFrame(columns=['quiz_type', 'avg_time', 'min_time', 'max_time'])
    
    # Filter out null time_spent values
    df_with_time = df[df['time_spent'].notna()]
    
    if df_with_time.empty:
        return pd.DataFrame(columns=['quiz_type', 'avg_time', 'min_time', 'max_time'])
    
    # Group by quiz type
    time_analysis = df_with_time.groupby('quiz_type')['time_spent'].agg([
        ('avg_time', 'mean'),
        ('min_time', 'min'),
        ('max_time', 'max'),
        ('median_time', 'median')
    ]).reset_index()
    
    # Convert seconds to minutes
    for col in ['avg_time', 'min_time', 'max_time', 'median_time']:
        time_analysis[col] = (time_analysis[col] / 60).round(2)
    
    return time_analysis
