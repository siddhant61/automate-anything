"""
Tests for quiz data transformation utilities.
"""

import pytest
import pandas as pd
import numpy as np

from src.analysis.quiz_transform import (
    transform_quiz_data,
    merge_quiz_data,
    clean_quiz_dataframe
)


class TestTransformQuizData:
    """Test quiz data transformation."""

    def test_transform_quiz_data_basic(self):
        """Test basic quiz transformation."""
        # Create sample data with question-option structure
        data = {
            'user_id': [1, 2, 3],
            'timestamp': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'course': ['python-101', 'python-101', 'python-101'],
            'quiz_type': ['start', 'start', 'start'],
            'score': [0, 0, 0],
            'Q1': [np.nan, np.nan, np.nan],  # Question marker (all NaN)
            'Q1_option_A': ['1', '0', '0'],  # User 1 selected this
            'Q1_option_B': ['0', '1', '0'],  # User 2 selected this
            'Q1_option_C': ['0', '0', '1'],  # User 3 selected this
            'Q2': [np.nan, np.nan, np.nan],  # Another question
            'Q2_yes': ['1', '0', '1'],
            'Q2_no': ['0', '1', '0'],
        }
        df = pd.DataFrame(data)
        
        result = transform_quiz_data(df)
        
        # Should have metadata columns + Q1 and Q2
        assert 'user_id' in result.columns
        assert 'Q1' in result.columns
        assert 'Q2' in result.columns
        
        # Check that selected options are recorded correctly
        assert result.loc[0, 'Q1'] == 'Q1_option_A'
        assert result.loc[1, 'Q1'] == 'Q1_option_B'
        assert result.loc[2, 'Q1'] == 'Q1_option_C'
        
        assert result.loc[0, 'Q2'] == 'Q2_yes'
        assert result.loc[1, 'Q2'] == 'Q2_no'
        assert result.loc[2, 'Q2'] == 'Q2_yes'

    def test_transform_quiz_data_empty(self):
        """Test transformation with empty DataFrame."""
        df = pd.DataFrame()
        result = transform_quiz_data(df)
        
        assert result.empty

    def test_transform_quiz_data_no_questions(self):
        """Test transformation when no questions detected."""
        # Data without question structure (no NaN marker columns)
        data = {
            'user_id': [1, 2],
            'timestamp': ['2024-01-01', '2024-01-02'],
            'score': [10, 20],
            'option_A': ['1', '0'],
            'option_B': ['0', '1'],
        }
        df = pd.DataFrame(data)
        
        result = transform_quiz_data(df)
        
        # Should return DataFrame with original columns (no transformation)
        assert len(result.columns) == len(df.columns)

    def test_transform_quiz_data_multiple_questions(self):
        """Test transformation with multiple questions."""
        data = {
            'user_id': [1, 2],
            'name': ['Alice', 'Bob'],
            'email': ['alice@test.com', 'bob@test.com'],
            'course': ['ml-101', 'ml-101'],
            'timestamp': ['2024-01-01', '2024-01-02'],
            'Q1': [np.nan, np.nan],
            'Q1_opt1': ['1', '0'],
            'Q1_opt2': ['0', '1'],
            'Q2': [np.nan, np.nan],
            'Q2_yes': ['1', '1'],
            'Q2_no': ['0', '0'],
            'Q3': [np.nan, np.nan],
            'Q3_a': ['0', '1'],
            'Q3_b': ['1', '0'],
        }
        df = pd.DataFrame(data)
        
        result = transform_quiz_data(df)
        
        # Should have 5 metadata columns + 3 question columns
        assert 'Q1' in result.columns
        assert 'Q2' in result.columns
        assert 'Q3' in result.columns
        
        # Verify data integrity
        assert len(result) == 2
        assert result.loc[0, 'user_id'] == 1
        assert result.loc[1, 'user_id'] == 2


class TestMergeQuizData:
    """Test quiz data merging."""

    def test_merge_quiz_data_success(self):
        """Test successful merge of start and end quiz data."""
        start_data = {
            'user_pseudo_id': ['user1', 'user2', 'user3'],
            'Q1_start': ['A', 'B', 'C'],
            'score_start': [5, 6, 7]
        }
        end_data = {
            'user_pseudo_id': ['user1', 'user2', 'user3'],
            'Q1_end': ['B', 'B', 'A'],
            'score_end': [8, 9, 10]
        }
        
        start_df = pd.DataFrame(start_data)
        end_df = pd.DataFrame(end_data)
        
        result = merge_quiz_data(start_df, end_df)
        
        assert len(result) == 3
        assert 'user_pseudo_id' in result.columns
        assert 'Q1_start_start' in result.columns or 'Q1_start' in result.columns
        assert 'Q1_end_end' in result.columns or 'Q1_end' in result.columns

    def test_merge_quiz_data_partial_overlap(self):
        """Test merge with partial user overlap."""
        start_data = {
            'user_pseudo_id': ['user1', 'user2', 'user3'],
            'score': [5, 6, 7]
        }
        end_data = {
            'user_pseudo_id': ['user2', 'user3', 'user4'],
            'score': [8, 9, 10]
        }
        
        start_df = pd.DataFrame(start_data)
        end_df = pd.DataFrame(end_data)
        
        result = merge_quiz_data(start_df, end_df)
        
        # Only user2 and user3 have both start and end data
        assert len(result) == 2

    def test_merge_quiz_data_missing_key(self):
        """Test merge with missing merge key."""
        start_df = pd.DataFrame({
            'user_id': ['user1', 'user2'],
            'score': [5, 6]
        })
        end_df = pd.DataFrame({
            'user_pseudo_id': ['user1', 'user2'],
            'score': [8, 9]
        })
        
        # start_df doesn't have user_pseudo_id
        result = merge_quiz_data(start_df, end_df)
        
        assert result.empty

    def test_merge_quiz_data_custom_key(self):
        """Test merge with custom merge key."""
        start_df = pd.DataFrame({
            'email': ['alice@test.com', 'bob@test.com'],
            'score_start': [5, 6]
        })
        end_df = pd.DataFrame({
            'email': ['alice@test.com', 'bob@test.com'],
            'score_end': [8, 9]
        })
        
        result = merge_quiz_data(start_df, end_df, merge_key='email')
        
        assert len(result) == 2
        assert 'email' in result.columns


class TestCleanQuizDataframe:
    """Test complete quiz cleaning workflow."""

    def test_clean_quiz_dataframe_full_workflow(self):
        """Test full cleaning workflow."""
        data = {
            'User ID': [1, 1, 2],  # Duplicate row for user 1
            'User Name': ['Alice', 'Alice', 'Bob'],
            'Course ID': ['py-101', 'py-101', 'py-101'],
            'Quiz Type': ['start', 'start', 'start'],
            'Timestamp': ['2024-01-01', '2024-01-01', '2024-01-02'],
            'Question 1': [np.nan, np.nan, np.nan],
            'Q1 Option A': ['1', '1', '0'],
            'Q1 Option B': ['0', '0', '1'],
        }
        df = pd.DataFrame(data)
        
        result = clean_quiz_dataframe(df)
        
        # Should remove duplicate
        assert len(result) == 2
        
        # Should have lowercase column names
        assert 'user_id' in result.columns
        assert 'user_name' in result.columns
        
        # Should have transformed questions
        assert 'question_1' in result.columns

    def test_clean_quiz_dataframe_empty(self):
        """Test cleaning empty DataFrame."""
        df = pd.DataFrame()
        result = clean_quiz_dataframe(df)
        
        assert result.empty

    def test_clean_quiz_dataframe_standardize_columns(self):
        """Test column name standardization."""
        data = {
            'User Name': ['Alice'],
            'Course Title': ['Python 101'],
            'Quiz Score': [85],
            'Time Spent': [120],
            'Question 1': [np.nan],
            'Q1 A': ['1'],
        }
        df = pd.DataFrame(data)
        
        result = clean_quiz_dataframe(df)
        
        # All columns should be lowercase with underscores
        for col in result.columns:
            assert col == col.lower()
            assert ' ' not in col
