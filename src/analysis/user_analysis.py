"""
User analysis module for survey grouping and teacher identification.

This module provides functionality to analyze survey responses and
identify specific user groups (e.g., teachers) from survey data.
"""

import pandas as pd
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models.tables import User, Survey, SurveyResponse


def find_teacher_users(
    db: Session,
    survey_ids: Optional[List[str]] = None,
    teacher_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Find users who identified as teachers in surveys.
    
    Args:
        db: Database session
        survey_ids: Optional list of survey IDs to filter
        teacher_columns: Optional list of column names that indicate teacher status
        
    Returns:
        DataFrame with teacher user data
    """
    # Default teacher-indicating column patterns
    if teacher_columns is None:
        teacher_columns = [
            'lehrkraft',
            'ich_bin_lehrkraft_und_betreue_meine_schler_innen_in_diesem_kurs',
            'ich_bin_lehrkraft_und_mchte_mir_den_kurs_anschauen'
        ]
    
    # Query survey responses
    query = select(SurveyResponse).join(User)
    
    if survey_ids:
        query = query.filter(SurveyResponse.survey_id.in_(survey_ids))
    
    responses = db.execute(query).scalars().all()
    
    # Convert to DataFrame
    data = []
    for response in responses:
        user = response.user
        data.append({
            'user_id': user.user_id if user else None,
            'user_name': user.full_name if user else None,
            'email': user.email if user else None,
            'survey_id': response.survey_id,
            'accessed_at': response.accessed_at,
            'submitted_at': response.submitted_at,
            'submit_duration': response.submit_duration,
            'points': response.points,
            'responses': response.responses  # JSON field with all responses
        })
    
    df = pd.DataFrame(data)
    
    if df.empty:
        return df
    
    # Filter for teacher responses
    teacher_data = []
    for _, row in df.iterrows():
        responses = row['responses']
        if responses and isinstance(responses, dict):
            # Check if any teacher-indicating field is set to '1' or True
            is_teacher = any(
                responses.get(col) in ['1', True, 'true', 'True']
                for col in teacher_columns
                if col in responses
            )
            
            if is_teacher:
                teacher_data.append(row)
    
    teacher_df = pd.DataFrame(teacher_data)
    
    # Remove duplicates based on user_id
    if not teacher_df.empty and 'user_id' in teacher_df.columns:
        teacher_df = teacher_df.drop_duplicates(subset=['user_id'])
    
    return teacher_df


def group_survey_responses_by_criteria(
    db: Session,
    survey_id: str,
    grouping_column: str
) -> Dict[str, pd.DataFrame]:
    """
    Group survey responses by a specific criteria column.
    
    Args:
        db: Database session
        survey_id: Survey identifier
        grouping_column: Column name to group by
        
    Returns:
        Dictionary mapping group values to DataFrames
    """
    # Query survey responses
    query = (
        select(SurveyResponse)
        .join(User)
        .filter(SurveyResponse.survey_id == survey_id)
    )
    
    responses = db.execute(query).scalars().all()
    
    # Convert to DataFrame
    data = []
    for response in responses:
        user = response.user
        responses_dict = response.responses or {}
        
        data.append({
            'user_id': user.user_id if user else None,
            'user_name': user.full_name if user else None,
            'email': user.email if user else None,
            'accessed_at': response.accessed_at,
            'submitted_at': response.submitted_at,
            'points': response.points,
            'grouping_value': responses_dict.get(grouping_column),
            **responses_dict
        })
    
    df = pd.DataFrame(data)
    
    if df.empty:
        return {}
    
    # Group by the specified column
    grouped = {}
    for value in df['grouping_value'].unique():
        if pd.notna(value):
            grouped[str(value)] = df[df['grouping_value'] == value].copy()
    
    return grouped


def analyze_survey_completion_rates(
    db: Session,
    survey_ids: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Analyze survey completion rates across different surveys.
    
    Args:
        db: Database session
        survey_ids: Optional list of survey IDs to analyze
        
    Returns:
        DataFrame with completion rate statistics
    """
    query = select(Survey)
    
    if survey_ids:
        query = query.filter(Survey.survey_id.in_(survey_ids))
    
    surveys = db.execute(query).scalars().all()
    
    results = []
    for survey in surveys:
        # Get responses for this survey
        responses_query = (
            select(SurveyResponse)
            .filter(SurveyResponse.survey_id == survey.survey_id)
        )
        responses = db.execute(responses_query).scalars().all()
        
        total_responses = len(responses)
        completed_responses = len([r for r in responses if r.submitted_at is not None])
        
        completion_rate = (
            (completed_responses / total_responses * 100)
            if total_responses > 0
            else 0
        )
        
        results.append({
            'survey_id': survey.survey_id,
            'survey_title': survey.title,
            'total_responses': total_responses,
            'completed_responses': completed_responses,
            'completion_rate': round(completion_rate, 2),
            'avg_points': sum(r.points or 0 for r in responses) / len(responses) if responses else 0
        })
    
    return pd.DataFrame(results)


def extract_user_segments_from_survey(
    db: Session,
    survey_id: str,
    segment_criteria: Dict[str, any]
) -> pd.DataFrame:
    """
    Extract user segments based on multiple criteria from survey responses.
    
    Args:
        db: Database session
        survey_id: Survey identifier
        segment_criteria: Dictionary of column names and expected values
        
    Returns:
        DataFrame with users matching the criteria
    """
    query = (
        select(SurveyResponse)
        .join(User)
        .filter(SurveyResponse.survey_id == survey_id)
    )
    
    responses = db.execute(query).scalars().all()
    
    # Convert to DataFrame
    data = []
    for response in responses:
        user = response.user
        responses_dict = response.responses or {}
        
        # Check if response matches all criteria
        matches = True
        for column, expected_value in segment_criteria.items():
            actual_value = responses_dict.get(column)
            
            if isinstance(expected_value, list):
                matches = matches and (actual_value in expected_value)
            else:
                matches = matches and (actual_value == expected_value)
        
        if matches:
            data.append({
                'user_id': user.user_id if user else None,
                'user_name': user.full_name if user else None,
                'email': user.email if user else None,
                'accessed_at': response.accessed_at,
                'submitted_at': response.submitted_at,
                'points': response.points,
                **responses_dict
            })
    
    df = pd.DataFrame(data)
    
    # Remove duplicates
    if not df.empty and 'user_id' in df.columns:
        df = df.drop_duplicates(subset=['user_id'])
    
    return df
