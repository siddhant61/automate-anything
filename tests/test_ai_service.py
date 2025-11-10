"""
Tests for AI service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import SecretStr
from src.services.ai_service import AIService, ai_service
from src.models.tables import Course


class TestAIService:
    """Test AI service functionality."""
    
    def test_ai_service_initialization_with_key(self):
        """Test AI service initializes correctly with API key."""
        with patch('src.services.ai_service.settings') as mock_settings:
            mock_settings.google_api_key = SecretStr("test_key")
            service = AIService()
            assert service.enabled is True
    
    def test_ai_service_initialization_without_key(self):
        """Test AI service initializes correctly without API key."""
        with patch('src.services.ai_service.settings') as mock_settings:
            mock_settings.google_api_key = SecretStr("")
            service = AIService()
            assert service.enabled is False
    
    def test_summarize_course_not_enabled(self):
        """Test course summarization when AI is not enabled."""
        service = AIService()
        service.enabled = False
        
        result = service.summarize_course("Test Course", "Test description")
        
        assert result['success'] is False
        assert 'not configured' in result['error']
        assert result['summary'] == ''
    
    @patch('src.services.ai_service.lf.query')
    def test_summarize_course_success(self, mock_query):
        """Test successful course summarization."""
        service = AIService()
        service.enabled = True
        
        mock_query.return_value = "This is a great course summary."
        
        result = service.summarize_course(
            "Python Basics",
            "Learn Python programming from scratch"
        )
        
        assert result['success'] is True
        assert result['title'] == "Python Basics"
        assert result['summary'] == "This is a great course summary."
        assert result['error'] is None
        mock_query.assert_called_once()
    
    @patch('src.services.ai_service.lf.query')
    def test_summarize_course_failure(self, mock_query):
        """Test course summarization failure handling."""
        service = AIService()
        service.enabled = True
        
        mock_query.side_effect = Exception("API error")
        
        result = service.summarize_course("Test", "Test description")
        
        assert result['success'] is False
        assert 'API error' in result['error']
        assert result['summary'] == ''
    
    def test_analyze_survey_feedback_not_enabled(self):
        """Test feedback analysis when AI is not enabled."""
        service = AIService()
        service.enabled = False
        
        result = service.analyze_survey_feedback(["Good course"])
        
        assert result['success'] is False
        assert 'not configured' in result['error']
    
    def test_analyze_survey_feedback_empty_list(self):
        """Test feedback analysis with empty feedback list."""
        service = AIService()
        service.enabled = True
        
        result = service.analyze_survey_feedback([])
        
        assert result['success'] is False
        assert 'No feedback texts' in result['error']
    
    @patch('src.services.ai_service.lf.query')
    def test_analyze_survey_feedback_success(self, mock_query):
        """Test successful feedback analysis."""
        service = AIService()
        service.enabled = True
        
        mock_query.return_value = "Overall positive sentiment with some suggestions"
        
        feedback = ["Great course!", "Could use more examples"]
        result = service.analyze_survey_feedback(feedback, context="Python course")
        
        assert result['success'] is True
        assert result['feedback_count'] == 2
        assert 'positive sentiment' in result['analysis']
        assert result['error'] is None
    
    @patch('src.services.ai_service.lf.query')
    def test_analyze_survey_feedback_with_context(self, mock_query):
        """Test feedback analysis with context."""
        service = AIService()
        service.enabled = True
        
        mock_query.return_value = "Analysis result"
        
        feedback = ["Excellent teaching"]
        context = "Teacher feedback for Java course"
        result = service.analyze_survey_feedback(feedback, context=context)
        
        assert result['success'] is True
        # Verify context is used in the prompt
        call_args = mock_query.call_args[0][0]
        assert context in call_args
    
    def test_extract_key_concepts_not_enabled(self):
        """Test concept extraction when AI is not enabled."""
        service = AIService()
        service.enabled = False
        
        result = service.extract_key_concepts("Course description")
        
        assert result['success'] is False
        assert 'not configured' in result['error']
        assert result['concepts'] == []
    
    @patch('src.services.ai_service.lf.query')
    def test_extract_key_concepts_success(self, mock_query):
        """Test successful key concept extraction."""
        service = AIService()
        service.enabled = True
        
        mock_query.return_value = "- Variables\n- Functions\n- Classes"
        
        result = service.extract_key_concepts("Learn Python programming")
        
        assert result['success'] is True
        assert 'Variables' in result['concepts']
        assert result['error'] is None
    
    def test_generate_course_insights_not_enabled(self):
        """Test course insights generation when AI is not enabled."""
        service = AIService()
        service.enabled = False
        
        mock_db = Mock()
        result = service.generate_course_insights(mock_db, "course123")
        
        assert result['success'] is False
        assert 'not configured' in result['error']
    
    def test_generate_course_insights_course_not_found(self):
        """Test course insights when course doesn't exist."""
        service = AIService()
        service.enabled = True
        
        mock_db = Mock()
        mock_db.query().filter().first.return_value = None
        
        result = service.generate_course_insights(mock_db, "nonexistent")
        
        assert result['success'] is False
        assert 'not found' in result['error']
    
    @patch('src.services.ai_service.lf.query')
    def test_generate_course_insights_success(self, mock_query):
        """Test successful course insights generation."""
        service = AIService()
        service.enabled = True
        
        # Mock course
        mock_course = Mock(spec=Course)
        mock_course.course_id = "python101"
        mock_course.title = "Python Basics"
        mock_course.description = "Learn Python programming"
        
        mock_db = Mock()
        mock_db.query().filter().first.return_value = mock_course
        
        # Mock AI responses
        mock_query.side_effect = [
            "A beginner-friendly Python course",  # summary
            "- Variables\n- Functions\n- Loops"   # concepts
        ]
        
        result = service.generate_course_insights(mock_db, "python101")
        
        assert result['success'] is True
        assert result['course_id'] == "python101"
        assert result['course_title'] == "Python Basics"
        assert 'Python course' in result['summary']
        assert 'Variables' in result['key_concepts']
        assert result['error'] is None
    
    def test_global_service_instance(self):
        """Test that global ai_service instance exists."""
        assert ai_service is not None
        assert isinstance(ai_service, AIService)


@pytest.mark.asyncio
class TestAIServiceIntegration:
    """Integration tests for AI service."""
    
    @patch('src.services.ai_service.settings')
    def test_service_respects_settings(self, mock_settings):
        """Test that service correctly uses settings."""
        mock_settings.google_api_key = SecretStr("test_key_123")
        
        service = AIService()
        
        # Service should be enabled with a key
        assert service.enabled is True
