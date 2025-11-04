"""
API endpoints for automation operations.

This module provides REST endpoints for batch enrollment,
helpdesk notifications, and page updates.
"""

from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.services.automation_service import automation_service

router = APIRouter()


class EnrollmentRequest(BaseModel):
    """Request model for batch enrollment."""
    users: List[str] = Field(..., description="List of user email addresses", min_items=1)
    course_id: str = Field(..., description="Course identifier")
    headless: bool = Field(default=True, description="Run browser in headless mode")


class PageUpdateRequest(BaseModel):
    """Request model for page update."""
    page_name: str = Field(..., description="Name of the page to update")
    content: str = Field(..., description="New content for the page")
    headless: bool = Field(default=True, description="Run browser in headless mode")


@router.post("/enroll")
async def batch_enroll_users(request: EnrollmentRequest):
    """
    Batch enroll users in a course.
    
    Request Body:
        users: List of user email addresses
        course_id: Course identifier
        headless: Whether to run browser in headless mode (default: True)
        
    Returns:
        Dictionary with enrolled and unregistered user lists
    """
    try:
        result = automation_service.batch_enroll_users(
            users=request.users,
            course_id=request.course_id,
            headless=request.headless
        )
        
        return {
            'success': True,
            'enrolled_count': len(result['enrolled']),
            'unregistered_count': len(result['unregistered']),
            'enrolled': result['enrolled'],
            'unregistered': result['unregistered']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrollment failed: {str(e)}")


@router.post("/notify-helpdesk")
async def notify_helpdesk():
    """
    Check helpdesk tickets and send notifications.
    
    Returns:
        Dictionary with ticket information and notification status
    """
    try:
        result = automation_service.check_and_notify_helpdesk(headless=True)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Helpdesk check failed: {str(e)}")


@router.post("/update-page")
async def update_page(request: PageUpdateRequest):
    """
    Update page content on OpenHPI platform.
    
    Request Body:
        page_name: Name of the page to update
        content: New content for the page
        headless: Whether to run browser in headless mode (default: True)
        
    Returns:
        Success status
    """
    try:
        success = automation_service.update_page(
            page_name=request.page_name,
            content=request.content,
            headless=request.headless
        )
        
        if success:
            return {
                'success': True,
                'message': f'Page "{request.page_name}" updated successfully'
            }
        else:
            raise HTTPException(status_code=500, detail="Page update failed")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Page update failed: {str(e)}")
