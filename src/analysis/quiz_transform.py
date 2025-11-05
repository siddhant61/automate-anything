"""
Quiz data transformation utilities.

This module provides functions to clean and transform quiz data before it's saved
to the database. Migrated from transform_quiz.py.
"""

import logging
from typing import Dict, List
import pandas as pd


logger = logging.getLogger(__name__)


def transform_quiz_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform quiz CSV data from wide format (one column per option) to long format 
    (one column per question with selected option value).
    
    This function handles quiz data where:
    - First 5 columns contain metadata (user info, timestamps, etc.)
    - Remaining columns are structured as: question_name (all NaN), option1, option2, ...
    - Selected options are marked with '1' in their respective columns
    
    Args:
        df: Raw quiz data DataFrame with columns structured as described above
        
    Returns:
        Transformed DataFrame with metadata columns + one column per question
        
    Example:
        Input columns: [user_id, timestamp, ..., Q1, Q1_opt1, Q1_opt2, Q2, Q2_opt1, ...]
        Where Q1 column has all NaN, and Q1_opt1/Q1_opt2 have '1' for selected options
        
        Output columns: [user_id, timestamp, ..., Q1, Q2, ...]
        Where Q1/Q2 contain the selected option text
    """
    if df.empty:
        logger.warning("Received empty DataFrame for transformation")
        return df
    
    columns = df.columns.tolist()
    
    # Identify question-option structure
    questions_corrected = {}
    current_question = None
    
    # Start from column 5 (skip metadata columns)
    for col in columns[5:]:
        # A column with all NaN values indicates a new question
        if df[col].isna().all():
            # Save previous question if it exists
            if current_question:
                questions_corrected[current_question['name']] = current_question['options']
            # Start new question
            current_question = {'name': col, 'options': []}
        else:
            # This is an option column for the current question
            if current_question:
                current_question['options'].append(col)
    
    # Don't forget the last question
    if current_question:
        questions_corrected[current_question['name']] = current_question['options']
    
    if not questions_corrected:
        logger.warning("No question-option structure detected in quiz data")
        return df
    
    # Transform the dataset
    # Keep first 5 metadata columns
    data_transformed = df.iloc[:, :5].copy()
    
    # For each question, create a single column with the selected option
    for question_name, option_columns in questions_corrected.items():
        # Initialize question column with NA
        data_transformed[question_name] = pd.NA
        
        # Find where each option is selected (marked with '1')
        for option_col in option_columns:
            # Set question value to the option name where that option is selected
            data_transformed.loc[df[option_col] == '1', question_name] = option_col
    
    logger.info(f"Transformed quiz data: {len(questions_corrected)} questions identified")
    
    return data_transformed


def merge_quiz_data(
    start_df: pd.DataFrame,
    end_df: pd.DataFrame,
    merge_key: str = "user_pseudo_id"
) -> pd.DataFrame:
    """
    Merge start and end quiz data for the same course.
    
    This combines pre-course and post-course quiz responses to enable
    learning progress analysis.
    
    Args:
        start_df: DataFrame with start-of-course quiz data
        end_df: DataFrame with end-of-course quiz data
        merge_key: Column name to merge on (default: user_pseudo_id)
        
    Returns:
        Merged DataFrame with both start and end quiz responses
    """
    if merge_key not in start_df.columns:
        logger.error(f"Merge key '{merge_key}' not found in start DataFrame")
        return pd.DataFrame()
    
    if merge_key not in end_df.columns:
        logger.error(f"Merge key '{merge_key}' not found in end DataFrame")
        return pd.DataFrame()
    
    try:
        combined = pd.merge(start_df, end_df, on=merge_key, suffixes=('_start', '_end'))
        logger.info(f"Merged quiz data: {len(combined)} users with both start and end responses")
        return combined
    except Exception as e:
        logger.error(f"Error merging quiz data: {e}")
        return pd.DataFrame()


def clean_quiz_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all cleaning transformations to quiz data.
    
    This is the main entry point for quiz data cleaning. It:
    1. Transforms from wide to long format
    2. Removes any duplicate rows
    3. Standardizes column names
    
    Args:
        df: Raw quiz DataFrame
        
    Returns:
        Cleaned and transformed DataFrame
    """
    # Transform from wide to long format
    df_transformed = transform_quiz_data(df)
    
    # Remove duplicates
    df_cleaned = df_transformed.drop_duplicates()
    
    # Standardize column names (lowercase, replace spaces with underscores)
    df_cleaned.columns = [col.lower().replace(' ', '_') for col in df_cleaned.columns]
    
    logger.info(f"Quiz data cleaning complete: {len(df_cleaned)} rows")
    
    return df_cleaned
