"""
User analysis module for survey grouping and teacher identification.

This module provides functionality to analyze survey responses and
identify specific user groups (e.g., teachers) from survey data.

Note: These functions work with the SurveyResponse table which stores
survey data in a flexible JSON format.
"""

import pandas as pd
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models.tables import User, SurveyResponse, Course


def find_teacher_users(
    db: Session,
    course_ids: Optional[List[str]] = None,
    survey_types: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Find users who identified as teachers in surveys.
    
    Args:
        db: Database session
        course_ids: Optional list of course IDs to filter
        survey_types: Optional list of survey types to filter (e.g., ['teacher'])
        
    Returns:
        DataFrame with teacher user data
    """
    # Query survey responses
    query = select(SurveyResponse)
    
    if course_ids:
        query = query.filter(SurveyResponse.course_id.in_(course_ids))
    
    if survey_types:
        query = query.filter(SurveyResponse.survey_type.in_(survey_types))
    else:
        # Default to teacher survey type
        query = query.filter(SurveyResponse.survey_type == 'teacher')
    
    responses = db.execute(query).scalars().all()
    
    # Convert to DataFrame
    data = []
    for response in responses:
        response_data = response.response_data or {}
        data.append({
            'course_id': response.course_id,
            'survey_type': response.survey_type,
            'submitted_at': response.submitted_at,
            'response_data': response_data
        })
    
    df = pd.DataFrame(data)
    
    # Remove duplicates based on course_id and survey_type
    if not df.empty:
        df = df.drop_duplicates(subset=['course_id', 'survey_type'])
    
    return df


def group_survey_responses_by_criteria(
    db: Session,
    course_id: str,
    survey_type: str,
    grouping_field: str
) -> Dict[str, pd.DataFrame]:
    """
    Group survey responses by a specific criteria field.
    
    Args:
        db: Database session
        course_id: Course identifier
        survey_type: Survey type (e.g., 'teacher', 'student')
        grouping_field: Field name in response_data JSON to group by
        
    Returns:
        Dictionary mapping group values to DataFrames
    """
    # Query survey responses
    query = (
        select(SurveyResponse)
        .filter(SurveyResponse.course_id == course_id)
        .filter(SurveyResponse.survey_type == survey_type)
    )
    
    responses = db.execute(query).scalars().all()
    
    # Convert to DataFrame
    data = []
    for response in responses:
        response_dict = response.response_data or {}
        
        data.append({
            'course_id': response.course_id,
            'survey_type': response.survey_type,
            'submitted_at': response.submitted_at,
            'grouping_value': response_dict.get(grouping_field),
            **response_dict
        })
    
    df = pd.DataFrame(data)
    
    if df.empty:
        return {}
    
    # Group by the specified field
    grouped = {}
    for value in df['grouping_value'].unique():
        if pd.notna(value):
            grouped[str(value)] = df[df['grouping_value'] == value].copy()
    
    return grouped


def analyze_survey_completion_rates(
    db: Session,
    course_ids: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Analyze survey completion rates across different courses and survey types.
    
    Args:
        db: Database session
        course_ids: Optional list of course IDs to analyze
        
    Returns:
        DataFrame with completion rate statistics
    """
    # Get unique combinations of course_id and survey_type
    query = select(SurveyResponse.course_id, SurveyResponse.survey_type).distinct()
    
    if course_ids:
        query = query.filter(SurveyResponse.course_id.in_(course_ids))
    
    unique_combinations = db.execute(query).all()
    
    results = []
    for course_id, survey_type in unique_combinations:
        # Get responses for this combination
        responses_query = (
            select(SurveyResponse)
            .filter(SurveyResponse.course_id == course_id)
            .filter(SurveyResponse.survey_type == survey_type)
        )
        responses = db.execute(responses_query).scalars().all()
        
        total_responses = len(responses)
        # All responses are considered completed if they have submitted_at
        completed_responses = len([r for r in responses if r.submitted_at is not None])
        
        completion_rate = (
            (completed_responses / total_responses * 100)
            if total_responses > 0
            else 0
        )
        
        results.append({
            'course_id': course_id,
            'survey_type': survey_type,
            'total_responses': total_responses,
            'completed_responses': completed_responses,
            'completion_rate': round(completion_rate, 2)
        })
    
    return pd.DataFrame(results)


def extract_user_segments_from_survey(
    db: Session,
    course_id: str,
    survey_type: str,
    segment_criteria: Dict[str, any]
) -> pd.DataFrame:
    """
    Extract user segments based on multiple criteria from survey responses.
    
    Args:
        db: Database session
        course_id: Course identifier
        survey_type: Survey type (e.g., 'teacher', 'student')
        segment_criteria: Dictionary of field names and expected values in response_data
        
    Returns:
        DataFrame with responses matching the criteria
    """
    query = (
        select(SurveyResponse)
        .filter(SurveyResponse.course_id == course_id)
        .filter(SurveyResponse.survey_type == survey_type)
    )
    
    responses = db.execute(query).scalars().all()
    
    # Convert to DataFrame
    data = []
    for response in responses:
        response_dict = response.response_data or {}
        
        # Check if response matches all criteria
        matches = True
        for field, expected_value in segment_criteria.items():
            actual_value = response_dict.get(field)
            
            if isinstance(expected_value, list):
                matches = matches and (actual_value in expected_value)
            else:
                matches = matches and (actual_value == expected_value)
        
        if matches:
            data.append({
                'course_id': response.course_id,
                'survey_type': response.survey_type,
                'submitted_at': response.submitted_at,
                **response_dict
            })
    
    df = pd.DataFrame(data)
    
    # Remove duplicates based on course_id
    if not df.empty and 'course_id' in df.columns:
        df = df.drop_duplicates(subset=['course_id'])
    
    return df
