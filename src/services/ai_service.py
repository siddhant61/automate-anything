"""
AI-powered analysis service using langfun and Google Generative AI.

This service provides AI-based course summaries, feedback analysis,
and insights generation using Google's Gemini models.
"""

import langfun as lf
import google.generativeai as genai
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from src.core.config import settings
from src.models.tables import Course, User


class AIService:
    """Service for AI-powered analysis and insights."""
    
    def __init__(self):
        """Initialize AI service with Google API configuration."""
        if settings.google_api_key:
            genai.configure(api_key=settings.google_api_key)
            self.enabled = True
        else:
            self.enabled = False
    
    def summarize_course(self, course_title: str, course_description: str) -> Dict[str, str]:
        """
        Generate a one-sentence summary of a course description.
        
        Args:
            course_title: Title of the course
            course_description: Full description of the course
            
        Returns:
            Dictionary with summary and status
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'AI service not configured. Please set GOOGLE_API_KEY.',
                'summary': ''
            }
        
        try:
            # Generate summary using langfun
            summary = lf.query(
                "Summarize the following course description in one sentence: {{description}}",
                lm=lf.llms.GeminiPro(),
                description=course_description
            )
            
            return {
                'success': True,
                'title': course_title,
                'summary': str(summary),
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'AI summary generation failed: {str(e)}',
                'summary': ''
            }
    
    def analyze_survey_feedback(
        self, 
        feedback_texts: List[str],
        context: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Analyze survey feedback using AI to extract insights.
        
        Args:
            feedback_texts: List of feedback text responses
            context: Optional context about the survey (e.g., "Teacher survey for Python course")
            
        Returns:
            Dictionary with insights and sentiment analysis
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'AI service not configured. Please set GOOGLE_API_KEY.',
                'insights': '',
                'sentiment': 'unknown'
            }
        
        if not feedback_texts:
            return {
                'success': False,
                'error': 'No feedback texts provided',
                'insights': '',
                'sentiment': 'unknown'
            }
        
        try:
            # Combine feedback texts
            combined_feedback = "\n".join([f"- {text}" for text in feedback_texts])
            
            # Create context-aware prompt
            prompt = f"""Analyze the following survey feedback{' for ' + context if context else ''}.
            
Feedback:
{combined_feedback}

Provide:
1. A summary of the main themes and insights
2. Overall sentiment (positive/neutral/negative)
3. Key recommendations based on the feedback

Format the response as JSON with keys: insights, sentiment, recommendations"""
            
            analysis = lf.query(
                prompt,
                lm=lf.llms.GeminiPro()
            )
            
            return {
                'success': True,
                'analysis': str(analysis),
                'feedback_count': len(feedback_texts),
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'AI feedback analysis failed: {str(e)}',
                'analysis': '',
                'feedback_count': len(feedback_texts)
            }
    
    def extract_key_concepts(self, course_description: str) -> Dict[str, any]:
        """
        Extract key concepts and topics from a course description.
        
        Args:
            course_description: Full description of the course
            
        Returns:
            Dictionary with key concepts list
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'AI service not configured. Please set GOOGLE_API_KEY.',
                'concepts': []
            }
        
        try:
            concepts = lf.query(
                """Extract the main topics and key concepts from this course description.
                List them as bullet points.
                
                Description: {{description}}""",
                lm=lf.llms.GeminiPro(),
                description=course_description
            )
            
            return {
                'success': True,
                'concepts': str(concepts),
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Concept extraction failed: {str(e)}',
                'concepts': []
            }
    
    def generate_course_insights(
        self, 
        db: Session,
        course_id: str
    ) -> Dict[str, any]:
        """
        Generate comprehensive insights for a course using AI.
        
        Args:
            db: Database session
            course_id: Course identifier
            
        Returns:
            Dictionary with AI-generated insights
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'AI service not configured. Please set GOOGLE_API_KEY.'
            }
        
        # Get course from database
        course = db.query(Course).filter(Course.course_id == course_id).first()
        
        if not course:
            return {
                'success': False,
                'error': f'Course {course_id} not found in database'
            }
        
        # Generate summary
        summary_result = self.summarize_course(
            course_title=course.title or course_id,
            course_description=course.description or "No description available"
        )
        
        # Extract key concepts
        concepts_result = self.extract_key_concepts(
            course_description=course.description or "No description available"
        )
        
        return {
            'success': True,
            'course_id': course_id,
            'course_title': course.title,
            'summary': summary_result.get('summary', ''),
            'key_concepts': concepts_result.get('concepts', []),
            'error': None
        }


# Global AI service instance
ai_service = AIService()
