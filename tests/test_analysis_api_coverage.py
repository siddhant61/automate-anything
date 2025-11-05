"""
Tests for analysis API endpoints to improve coverage.
"""

import pytest
from unittest.mock import patch, Mock
import pandas as pd
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestCourseMetricsEndpoint:
    """Test course metrics endpoint."""

    @patch('src.api.analysis.course_analytics.prepare_visualization_data')
    def test_get_course_metrics_success(self, mock_prepare, client):
        """Test successful course metrics retrieval."""
        mock_prepare.return_value = {
            'monthly_enrollments': pd.DataFrame({'month': [1, 2], 'count': [10, 20]}),
            'metrics': {
                'total': 30,
                'completion_rate': 75.0
            },
            'certificates': {'CoD': 10, 'RoA': 5}
        }
        
        response = client.get("/api/analysis/course_metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'monthly_enrollments' in data
        assert 'metrics' in data
        assert 'certificates' in data

    @patch('src.api.analysis.course_analytics.prepare_visualization_data')
    def test_get_course_metrics_with_filters(self, mock_prepare, client):
        """Test course metrics with year and category filters."""
        mock_prepare.return_value = {
            'monthly_enrollments': pd.DataFrame(),
            'metrics': {},
            'certificates': {}
        }
        
        response = client.get("/api/analysis/course_metrics?years=2023&years=2024&categories=Java&categories=Python")
        
        assert response.status_code == 200
        mock_prepare.assert_called_once()

    @patch('src.api.analysis.course_analytics.prepare_visualization_data')
    def test_get_course_metrics_error(self, mock_prepare, client):
        """Test course metrics with error."""
        mock_prepare.side_effect = Exception("Database error")
        
        response = client.get("/api/analysis/course_metrics")
        
        assert response.status_code == 500
        assert 'error' in response.json()['detail'].lower()


class TestAnnualStatsEndpoint:
    """Test annual stats endpoint."""

    @patch('src.api.analysis.annual_stats.generate_annual_report')
    def test_get_annual_stats_success(self, mock_generate, client):
        """Test successful annual stats retrieval."""
        mock_generate.return_value = {
            'year': 2024,
            'metrics': {
                'total_enrollments': 1000,
                'total_certificates': 500
            }
        }
        
        response = client.get("/api/analysis/annual_stats/2024")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'report' in data

    @patch('src.api.analysis.annual_stats.generate_annual_report')
    def test_get_annual_stats_error(self, mock_generate, client):
        """Test annual stats with error."""
        mock_generate.side_effect = Exception("Report generation failed")
        
        response = client.get("/api/analysis/annual_stats/2024")
        
        assert response.status_code == 500
        assert 'error' in response.json()['detail'].lower()


class TestQuizPerformanceEndpoint:
    """Test quiz performance endpoint."""

    @patch('src.api.analysis.quiz_analytics.load_quiz_data_from_db')
    @patch('src.api.analysis.quiz_analytics.calculate_quiz_performance_metrics')
    @patch('src.api.analysis.quiz_analytics.get_quiz_performance_by_course')
    @patch('src.api.analysis.quiz_analytics.get_quiz_performance_by_type')
    @patch('src.api.analysis.quiz_analytics.get_quiz_time_analysis')
    def test_get_quiz_performance_success(self, mock_time, mock_by_type, mock_by_course, 
                                         mock_metrics, mock_load, client):
        """Test successful quiz performance retrieval."""
        mock_load.return_value = pd.DataFrame({'quiz_id': [1, 2], 'score': [80, 90]})
        mock_metrics.return_value = {'avg_score': 85.0, 'pass_rate': 90.0}
        mock_by_course.return_value = pd.DataFrame({'course': ['A', 'B'], 'avg': [80, 90]})
        mock_by_type.return_value = pd.DataFrame({'type': ['graded'], 'avg': [85]})
        mock_time.return_value = pd.DataFrame({'month': [1], 'avg': [85]})
        
        response = client.get("/api/analysis/quiz_performance")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'overall_metrics' in data
        assert 'by_course' in data
        assert 'by_type' in data
        assert 'time_analysis' in data

    @patch('src.api.analysis.quiz_analytics.load_quiz_data_from_db')
    @patch('src.api.analysis.quiz_analytics.calculate_quiz_performance_metrics')
    @patch('src.api.analysis.quiz_analytics.get_quiz_performance_by_course')
    @patch('src.api.analysis.quiz_analytics.get_quiz_performance_by_type')
    @patch('src.api.analysis.quiz_analytics.get_quiz_time_analysis')
    def test_get_quiz_performance_with_filters(self, mock_time, mock_by_type, mock_by_course,
                                              mock_metrics, mock_load, client):
        """Test quiz performance with filters."""
        mock_load.return_value = pd.DataFrame()
        mock_metrics.return_value = {}
        mock_by_course.return_value = pd.DataFrame()
        mock_by_type.return_value = pd.DataFrame()
        mock_time.return_value = pd.DataFrame()
        
        response = client.get("/api/analysis/quiz_performance?course_ids=course1&course_ids=course2&quiz_type=graded")
        
        assert response.status_code == 200
        mock_load.assert_called_once()

    @patch('src.api.analysis.quiz_analytics.load_quiz_data_from_db')
    def test_get_quiz_performance_error(self, mock_load, client):
        """Test quiz performance with error."""
        mock_load.side_effect = Exception("Query failed")
        
        response = client.get("/api/analysis/quiz_performance")
        
        assert response.status_code == 500
        assert 'error' in response.json()['detail'].lower()


class TestQuizComparisonEndpoint:
    """Test quiz comparison endpoint."""

    def test_compare_quiz_insufficient_courses(self, client):
        """Test quiz comparison with insufficient courses."""
        response = client.get("/api/analysis/quiz_comparison?course_ids=course1")
        
        assert response.status_code == 400
        assert 'at least 2' in response.json()['detail'].lower()

    def test_compare_quiz_no_courses(self, client):
        """Test quiz comparison with no courses."""
        response = client.get("/api/analysis/quiz_comparison")
        
        assert response.status_code == 422  # Validation error

    @patch('src.api.analysis.quiz_analytics.compare_quiz_performance')
    def test_compare_quiz_success(self, mock_compare, client):
        """Test successful quiz comparison."""
        mock_compare.return_value = {
            'course1': {'avg_score': 80},
            'course2': {'avg_score': 85}
        }
        
        response = client.get("/api/analysis/quiz_comparison?course_ids=course1&course_ids=course2")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'comparison' in data

    @patch('src.api.analysis.quiz_analytics.compare_quiz_performance')
    def test_compare_quiz_error(self, mock_compare, client):
        """Test quiz comparison with error."""
        mock_compare.side_effect = Exception("Comparison failed")
        
        response = client.get("/api/analysis/quiz_comparison?course_ids=course1&course_ids=course2")
        
        assert response.status_code == 500
        assert 'error' in response.json()['detail'].lower()


class TestEnrollmentTrendsEndpoint:
    """Test enrollment trends endpoint."""

    @patch('src.api.analysis.course_analytics.load_enrollment_data_from_db')
    @patch('src.api.analysis.course_analytics.get_monthly_enrollments')
    def test_get_enrollment_trends_success(self, mock_monthly, mock_load, client):
        """Test successful enrollment trends retrieval."""
        mock_load.return_value = pd.DataFrame({'course_id': [1], 'category': ['Java']})
        mock_monthly.return_value = pd.DataFrame({'month': [1], 'count': [10]})
        
        response = client.get("/api/analysis/enrollment_trends")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'monthly_enrollments' in data

    @patch('src.api.analysis.course_analytics.load_enrollment_data_from_db')
    @patch('src.api.analysis.course_analytics.get_monthly_enrollments')
    def test_get_enrollment_trends_with_filters(self, mock_monthly, mock_load, client):
        """Test enrollment trends with filters."""
        mock_load.return_value = pd.DataFrame({'course_id': [1], 'category': ['Java']})
        mock_monthly.return_value = pd.DataFrame()
        
        response = client.get("/api/analysis/enrollment_trends?years=2024&categories=Java")
        
        assert response.status_code == 200
        mock_load.assert_called_once()

    @patch('src.api.analysis.course_analytics.load_enrollment_data_from_db')
    def test_get_enrollment_trends_error(self, mock_load, client):
        """Test enrollment trends with error."""
        mock_load.side_effect = Exception("Database error")
        
        response = client.get("/api/analysis/enrollment_trends")
        
        assert response.status_code == 500
        assert 'error' in response.json()['detail'].lower()


class TestTeacherSurveysEndpoint:
    """Test teacher surveys endpoint."""

    @patch('src.analysis.user_analysis.find_teacher_users')
    def test_get_teacher_surveys_success(self, mock_find, client):
        """Test successful teacher surveys retrieval."""
        mock_find.return_value = pd.DataFrame({
            'user_id': [1, 2],
            'email': ['teacher1@test.com', 'teacher2@test.com']
        })
        
        response = client.get("/api/analysis/teacher_surveys")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['count'] == 2
        assert 'surveys' in data

    @patch('src.analysis.user_analysis.find_teacher_users')
    def test_get_teacher_surveys_with_filters(self, mock_find, client):
        """Test teacher surveys with course filters."""
        mock_find.return_value = pd.DataFrame()
        
        response = client.get("/api/analysis/teacher_surveys?course_ids=course1&course_ids=course2")
        
        assert response.status_code == 200
        mock_find.assert_called_once()

    @patch('src.analysis.user_analysis.find_teacher_users')
    def test_get_teacher_surveys_error(self, mock_find, client):
        """Test teacher surveys with error."""
        mock_find.side_effect = Exception("Query failed")
        
        response = client.get("/api/analysis/teacher_surveys")
        
        assert response.status_code == 500
        assert 'error' in response.json()['detail'].lower()


class TestSurveyCompletionEndpoint:
    """Test survey completion endpoint."""

    @patch('src.analysis.user_analysis.analyze_survey_completion_rates')
    def test_get_survey_completion_success(self, mock_analyze, client):
        """Test successful survey completion retrieval."""
        mock_analyze.return_value = pd.DataFrame({
            'course_id': ['course1'],
            'completion_rate': [75.0]
        })
        
        response = client.get("/api/analysis/survey_completion")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'surveys' in data

    @patch('src.analysis.user_analysis.analyze_survey_completion_rates')
    def test_get_survey_completion_with_filters(self, mock_analyze, client):
        """Test survey completion with filters."""
        mock_analyze.return_value = pd.DataFrame()
        
        response = client.get("/api/analysis/survey_completion?course_ids=course1")
        
        assert response.status_code == 200
        mock_analyze.assert_called_once()

    @patch('src.analysis.user_analysis.analyze_survey_completion_rates')
    def test_get_survey_completion_error(self, mock_analyze, client):
        """Test survey completion with error."""
        mock_analyze.side_effect = Exception("Analysis failed")
        
        response = client.get("/api/analysis/survey_completion")
        
        assert response.status_code == 500
        assert 'error' in response.json()['detail'].lower()
