"""
Tests for AI API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from src.main import app


client = TestClient(app)


class TestAIAPI:
    """Test AI API endpoints."""
    
    @patch('src.api.ai.ai_service')
    def test_summarize_course_success(self, mock_ai_service):
        """Test successful course summarization."""
        mock_ai_service.summarize_course.return_value = {
            'success': True,
            'title': 'Python Basics',
            'summary': 'A comprehensive introduction to Python programming.',
            'error': None
        }
        
        response = client.post(
            "/api/ai/summarize-course",
            json={
                "course_title": "Python Basics",
                "course_description": "Learn Python programming from scratch"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['title'] == 'Python Basics'
        assert 'Python programming' in data['summary']
    
    @patch('src.api.ai.ai_service')
    def test_summarize_course_failure(self, mock_ai_service):
        """Test course summarization failure."""
        mock_ai_service.summarize_course.return_value = {
            'success': False,
            'error': 'AI service not configured',
            'summary': ''
        }
        
        response = client.post(
            "/api/ai/summarize-course",
            json={
                "course_title": "Test",
                "course_description": "Test description"
            }
        )
        
        assert response.status_code == 500
        assert 'not configured' in response.json()['detail']
    
    def test_summarize_course_invalid_request(self):
        """Test course summarization with invalid request."""
        response = client.post(
            "/api/ai/summarize-course",
            json={
                "course_title": "Test"
                # Missing course_description
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('src.api.ai.ai_service')
    def test_analyze_feedback_success(self, mock_ai_service):
        """Test successful feedback analysis."""
        mock_ai_service.analyze_survey_feedback.return_value = {
            'success': True,
            'analysis': 'Overall positive sentiment with constructive feedback',
            'feedback_count': 3,
            'error': None
        }
        
        response = client.post(
            "/api/ai/analyze-feedback",
            json={
                "feedback_texts": [
                    "Great course!",
                    "Very helpful content",
                    "Could use more examples"
                ],
                "context": "Python course feedback"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['feedback_count'] == 3
        assert 'positive' in data['analysis']
    
    @patch('src.api.ai.ai_service')
    def test_analyze_feedback_without_context(self, mock_ai_service):
        """Test feedback analysis without context."""
        mock_ai_service.analyze_survey_feedback.return_value = {
            'success': True,
            'analysis': 'Analysis result',
            'feedback_count': 2,
            'error': None
        }
        
        response = client.post(
            "/api/ai/analyze-feedback",
            json={
                "feedback_texts": ["Good", "Bad"]
            }
        )
        
        assert response.status_code == 200
        # Verify context was None
        mock_ai_service.analyze_survey_feedback.assert_called_once()
        call_kwargs = mock_ai_service.analyze_survey_feedback.call_args[1]
        assert call_kwargs['context'] is None
    
    @patch('src.api.ai.ai_service')
    def test_analyze_feedback_failure(self, mock_ai_service):
        """Test feedback analysis failure with service error."""
        mock_ai_service.analyze_survey_feedback.return_value = {
            'success': False,
            'error': 'AI service error',
            'analysis': '',
            'feedback_count': 1
        }
        
        response = client.post(
            "/api/ai/analyze-feedback",
            json={
                "feedback_texts": ["Some feedback"]
            }
        )
        
        assert response.status_code == 500
    
    def test_analyze_feedback_invalid_request(self):
        """Test feedback analysis with invalid request."""
        response = client.post(
            "/api/ai/analyze-feedback",
            json={
                # Missing feedback_texts
                "context": "Test"
            }
        )
        
        assert response.status_code == 422
    
    def test_analyze_feedback_empty_list(self):
        """Test feedback analysis with empty list (should fail validation)."""
        response = client.post(
            "/api/ai/analyze-feedback",
            json={
                "feedback_texts": []
            }
        )
        
        # Empty list should fail validation (min_length=1)
        assert response.status_code in [422, 500]
    
    @patch('src.api.ai.ai_service')
    def test_get_course_insights_success(self, mock_ai_service, test_db):
        """Test successful course insights generation."""
        mock_ai_service.generate_course_insights.return_value = {
            'success': True,
            'course_id': 'python101',
            'course_title': 'Python Basics',
            'summary': 'A beginner-friendly course',
            'key_concepts': '- Variables\n- Functions\n- Loops',
            'error': None
        }
        
        response = client.get("/api/ai/course-insights/python101")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['course_id'] == 'python101'
        assert 'Variables' in data['key_concepts']
    
    @patch('src.api.ai.ai_service')
    def test_get_course_insights_not_found(self, mock_ai_service):
        """Test course insights for non-existent course."""
        mock_ai_service.generate_course_insights.return_value = {
            'success': False,
            'error': 'Course nonexistent not found in database'
        }
        
        response = client.get("/api/ai/course-insights/nonexistent")
        
        assert response.status_code == 404
        assert 'not found' in response.json()['detail']
    
    @patch('src.api.ai.ai_service')
    def test_get_course_insights_ai_error(self, mock_ai_service):
        """Test course insights with AI error."""
        mock_ai_service.generate_course_insights.return_value = {
            'success': False,
            'error': 'AI service error occurred'
        }
        
        response = client.get("/api/ai/course-insights/python101")
        
        assert response.status_code == 500
    
    @patch('src.api.ai.ai_service')
    def test_ai_health_check_enabled(self, mock_ai_service):
        """Test AI health check when service is enabled."""
        mock_ai_service.enabled = True
        
        response = client.get("/api/ai/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['enabled'] is True
        assert data['status'] == 'configured'
        assert 'ready' in data['message']
    
    @patch('src.api.ai.ai_service')
    def test_ai_health_check_disabled(self, mock_ai_service):
        """Test AI health check when service is not configured."""
        mock_ai_service.enabled = False
        
        response = client.get("/api/ai/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['enabled'] is False
        assert data['status'] == 'not_configured'
        assert 'GOOGLE_API_KEY' in data['message']


@pytest.mark.asyncio
class TestAIAPIIntegration:
    """Integration tests for AI API."""
    
    @patch('src.api.ai.ai_service')
    def test_full_workflow(self, mock_ai_service):
        """Test complete AI workflow."""
        mock_ai_service.enabled = True
        
        # 1. Check health
        health = client.get("/api/ai/health")
        assert health.status_code == 200
        assert health.json()['enabled'] is True
        
        # 2. Summarize a course
        mock_ai_service.summarize_course.return_value = {
            'success': True,
            'title': 'Test Course',
            'summary': 'Test summary',
            'error': None
        }
        
        summary = client.post(
            "/api/ai/summarize-course",
            json={
                "course_title": "Test Course",
                "course_description": "Test description"
            }
        )
        assert summary.status_code == 200
        
        # 3. Analyze feedback
        mock_ai_service.analyze_survey_feedback.return_value = {
            'success': True,
            'analysis': 'Test analysis',
            'feedback_count': 1,
            'error': None
        }
        
        feedback = client.post(
            "/api/ai/analyze-feedback",
            json={
                "feedback_texts": ["Good course"]
            }
        )
        assert feedback.status_code == 200
