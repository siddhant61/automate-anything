"""
API endpoints for AI-powered analysis.

This module provides REST endpoints for AI-based course summaries,
feedback analysis, and insights generation.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.services.ai_service import ai_service

router = APIRouter()


class CourseSummaryRequest(BaseModel):
    """Request model for course summary."""
    course_title: str = Field(..., description="Title of the course")
    course_description: str = Field(..., description="Description of the course")


class FeedbackAnalysisRequest(BaseModel):
    """Request model for feedback analysis."""
    feedback_texts: List[str] = Field(..., description="List of feedback texts", min_length=1)
    context: Optional[str] = Field(None, description="Optional context about the feedback")


@router.post("/summarize-course")
async def summarize_course(request: CourseSummaryRequest):
    """
    Generate a one-sentence summary of a course description using AI.
    
    Request Body:
        course_title: Title of the course
        course_description: Full description of the course
        
    Returns:
        AI-generated summary
    """
    result = ai_service.summarize_course(
        course_title=request.course_title,
        course_description=request.course_description
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result['error'])
    
    return result


@router.post("/analyze-feedback")
async def analyze_feedback(request: FeedbackAnalysisRequest):
    """
    Analyze survey feedback using AI to extract insights and sentiment.
    
    Request Body:
        feedback_texts: List of feedback text responses
        context: Optional context about the survey
        
    Returns:
        AI-generated insights and sentiment analysis
    """
    result = ai_service.analyze_survey_feedback(
        feedback_texts=request.feedback_texts,
        context=request.context
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result['error'])
    
    return result


@router.get("/course-insights/{course_id}")
async def get_course_insights(
    course_id: str,
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive AI insights for a course.
    
    Path Parameters:
        course_id: Course identifier
        
    Returns:
        AI-generated summary, key concepts, and insights
    """
    result = ai_service.generate_course_insights(
        db=db,
        course_id=course_id
    )
    
    if not result['success']:
        raise HTTPException(status_code=404 if 'not found' in result['error'] else 500, 
                          detail=result['error'])
    
    return result


@router.get("/health")
async def ai_health_check():
    """
    Check if AI service is configured and available.
    
    Returns:
        Status of AI service
    """
    return {
        'enabled': ai_service.enabled,
        'status': 'configured' if ai_service.enabled else 'not_configured',
        'message': 'AI service is ready' if ai_service.enabled else 'Set GOOGLE_API_KEY to enable AI features'
    }
