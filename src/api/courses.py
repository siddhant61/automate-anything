"""
API endpoints for course operations.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
import tempfile

from src.models.database import get_db
from src.models.tables import Course, CourseStats
from src.services.course_parser_service import course_parser_service
from src.core.config import settings

router = APIRouter()


class CourseParseRequest(BaseModel):
    """Request model for course parsing."""
    org: str = "HPI"
    course_id: str = "course"
    url_name: str = "2024"


@router.get("/")
async def list_courses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    language: Optional[str] = Query(None, description="Filter by language"),
    db: Session = Depends(get_db)
):
    """
    List all courses with optional filtering.
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        category: Filter by course category (e.g., "Java", "Python")
        language: Filter by language (e.g., "en", "de")
        
    Returns:
        List of courses
    """
    query = db.query(Course)
    
    # Apply filters
    if category:
        query = query.filter(Course.category == category)
    if language:
        query = query.filter(Course.language == language)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    courses = query.offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "total": total,
        "skip": skip,
        "limit": limit,
        "count": len(courses),
        "courses": [
            {
                "id": course.id,
                "course_id": course.course_id,
                "title": course.title,
                "description": course.description,
                "url": course.url,
                "language": course.language,
                "category": course.category,
                "start_date": course.start_date.isoformat() if course.start_date else None,
                "end_date": course.end_date.isoformat() if course.end_date else None,
                "created_at": course.created_at.isoformat() if course.created_at else None,
            }
            for course in courses
        ]
    }


@router.get("/{course_id}")
async def get_course(
    course_id: str,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific course.
    
    Args:
        course_id: Course identifier
        
    Returns:
        Course details
    """
    course = db.query(Course).filter_by(course_id=course_id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return {
        "success": True,
        "course": {
            "id": course.id,
            "course_id": course.course_id,
            "title": course.title,
            "description": course.description,
            "url": course.url,
            "language": course.language,
            "category": course.category,
            "start_date": course.start_date.isoformat() if course.start_date else None,
            "end_date": course.end_date.isoformat() if course.end_date else None,
            "created_at": course.created_at.isoformat() if course.created_at else None,
            "updated_at": course.updated_at.isoformat() if course.updated_at else None,
        }
    }


@router.get("/{course_id}/stats")
async def get_course_stats(
    course_id: str,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific course.
    
    Args:
        course_id: Course identifier
        
    Returns:
        Course statistics (all historical records)
    """
    course = db.query(Course).filter_by(course_id=course_id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    stats = db.query(CourseStats)\
        .filter_by(course_id=course_id)\
        .order_by(CourseStats.recorded_at.desc())\
        .all()
    
    return {
        "success": True,
        "course_id": course_id,
        "course_title": course.title,
        "stats_count": len(stats),
        "stats": [
            {
                "id": stat.id,
                "recorded_at": stat.recorded_at.isoformat() if stat.recorded_at else None,
                "year": stat.year,
                "total_enrollments": stat.total_enrollments,
                "active_users": stat.active_users,
                "certificates_issued": stat.certificates_issued,
                "completion_rate": stat.completion_rate,
                "average_progress": stat.average_progress,
                "average_session_duration": stat.average_session_duration,
                "items_visited_percentage": stat.items_visited_percentage,
                "graded_quiz_performance": stat.graded_quiz_performance,
                "ungraded_quiz_performance": stat.ungraded_quiz_performance,
            }
            for stat in stats
        ]
    }


@router.get("/categories/list")
async def list_categories(db: Session = Depends(get_db)):
    """
    Get list of all unique course categories.
    
    Returns:
        List of categories
    """
    categories = db.query(Course.category)\
        .filter(Course.category.isnot(None))\
        .distinct()\
        .all()
    
    return {
        "success": True,
        "count": len(categories),
        "categories": [cat[0] for cat in categories if cat[0]]
    }


@router.post("/parse-edx")
async def parse_edx_course(
    file: UploadFile = File(..., description="JSON file with EdX course data"),
    org: str = Query("HPI", description="Organization identifier"),
    course_id: str = Query("course", description="Course identifier"),
    url_name: str = Query("2024", description="URL name for the course")
):
    """
    Parse EdX course data and generate OpenHPI-compatible structure.
    
    Args:
        file: JSON file containing course data
        org: Organization identifier
        course_id: Course identifier
        url_name: URL name for the course
        
    Returns:
        Parsing results with generated file paths
    """
    try:
        # Read uploaded file
        content = await file.read()
        course_data = json.loads(content)
        
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Parse course structure
            result = course_parser_service.parse_course_structure(
                course_data=course_data,
                output_dir=temp_dir,
                org=org,
                course_id=course_id,
                url_name=url_name
            )
            
            # Copy to exports directory
            import shutil
            final_output = settings.exports_dir / "course_exports"
            final_output.mkdir(parents=True, exist_ok=True)
            
            tar_filename = f"{course_id}_{url_name}.tar.gz"
            final_tar_path = final_output / tar_filename
            
            shutil.copy2(result['tar_path'], final_tar_path)
            
            return {
                'success': True,
                'message': 'Course parsed successfully',
                'output_file': str(final_tar_path),
                'statistics': {
                    'chapters': result['chapters'],
                    'sequentials': result['sequentials'],
                    'verticals': result['verticals']
                }
            }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Course parsing failed: {str(e)}")
