"""
API endpoints for analysis operations.

This module provides REST endpoints for course analytics, annual statistics,
and quiz performance analysis.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.analysis import course_analytics, annual_stats, quiz_analytics

router = APIRouter()


@router.get("/course_metrics")
async def get_course_metrics(
    years: Optional[List[int]] = Query(None, description="Filter by years"),
    categories: Optional[List[str]] = Query(None, description="Filter by categories (e.g., Java, Python)"),
    db: Session = Depends(get_db)
):
    """
    Get course performance metrics.
    
    Query Parameters:
        years: Optional list of years to include
        categories: Optional list of categories to filter
        
    Returns:
        Course metrics including enrollments, certificates, and completion rates
    """
    try:
        data = course_analytics.prepare_visualization_data(
            db=db,
            years=years,
            categories=categories
        )
        
        # Convert DataFrames to JSON-serializable format
        result = {
            'success': True,
            'monthly_enrollments': data['monthly_enrollments'].to_dict() if not data['monthly_enrollments'].empty else {},
            'metrics': {
                key: value.to_dict() if hasattr(value, 'to_dict') else value
                for key, value in data['metrics'].items()
            },
            'certificates': data['certificates'].to_dict() if hasattr(data['certificates'], 'to_dict') else data['certificates'],
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating course metrics: {str(e)}")


@router.get("/annual_stats/{year}")
async def get_annual_stats(
    year: int,
    db: Session = Depends(get_db)
):
    """
    Get annual statistics report for a specific year.
    
    Path Parameters:
        year: Year to generate report for
        
    Returns:
        Annual report with enrollments, certificates, and completion rates
    """
    try:
        report = annual_stats.generate_annual_report(db=db, year=year)
        return {
            'success': True,
            'report': report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating annual report: {str(e)}")


@router.get("/quiz_performance")
async def get_quiz_performance(
    course_ids: Optional[List[str]] = Query(None, description="Filter by course IDs"),
    quiz_type: Optional[str] = Query(None, description="Filter by quiz type (graded/ungraded/survey)"),
    db: Session = Depends(get_db)
):
    """
    Get quiz performance metrics.
    
    Query Parameters:
        course_ids: Optional list of course IDs to filter
        quiz_type: Optional quiz type filter
        
    Returns:
        Quiz performance metrics including average scores, pass rates, etc.
    """
    try:
        # Load quiz data
        df = quiz_analytics.load_quiz_data_from_db(
            db=db,
            course_ids=course_ids,
            quiz_type=quiz_type
        )
        
        # Calculate metrics
        overall_metrics = quiz_analytics.calculate_quiz_performance_metrics(df)
        performance_by_course = quiz_analytics.get_quiz_performance_by_course(df)
        performance_by_type = quiz_analytics.get_quiz_performance_by_type(df)
        time_analysis = quiz_analytics.get_quiz_time_analysis(df)
        
        return {
            'success': True,
            'overall_metrics': overall_metrics,
            'by_course': performance_by_course.to_dict('records'),
            'by_type': performance_by_type.to_dict('records'),
            'time_analysis': time_analysis.to_dict('records'),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing quiz performance: {str(e)}")


@router.get("/quiz_comparison")
async def compare_quiz_performance(
    course_ids: List[str] = Query(..., description="List of course IDs to compare"),
    db: Session = Depends(get_db)
):
    """
    Compare quiz performance across multiple courses.
    
    Query Parameters:
        course_ids: List of course IDs to compare (required)
        
    Returns:
        Comparison of quiz performance metrics across courses
    """
    if not course_ids or len(course_ids) < 2:
        raise HTTPException(
            status_code=400, 
            detail="At least 2 course IDs are required for comparison"
        )
    
    try:
        comparison = quiz_analytics.compare_quiz_performance(
            db=db,
            course_ids=course_ids
        )
        
        return {
            'success': True,
            'comparison': comparison
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing quiz performance: {str(e)}")


@router.get("/enrollment_trends")
async def get_enrollment_trends(
    years: Optional[List[int]] = Query(None, description="Filter by years"),
    categories: Optional[List[str]] = Query(None, description="Filter by categories"),
    db: Session = Depends(get_db)
):
    """
    Get enrollment trend data for visualization.
    
    Query Parameters:
        years: Optional list of years to include
        categories: Optional list of categories to filter
        
    Returns:
        Enrollment trend data grouped by month
    """
    try:
        # Load enrollment data
        df = course_analytics.load_enrollment_data_from_db(
            db=db,
            years=years
        )
        
        if not df.empty and categories:
            df = df[df['category'].isin(categories)]
        
        # Get monthly enrollments
        monthly = course_analytics.get_monthly_enrollments(df)
        
        return {
            'success': True,
            'monthly_enrollments': monthly.to_dict() if not monthly.empty else {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating enrollment trends: {str(e)}")


@router.get("/teacher_surveys")
async def get_teacher_surveys(
    course_ids: Optional[List[str]] = Query(None, description="Filter by course IDs"),
    db: Session = Depends(get_db)
):
    """
    Get teacher survey responses.
    
    Query Parameters:
        course_ids: Optional list of course IDs to filter
        
    Returns:
        List of teacher survey responses
    """
    try:
        from src.analysis import user_analysis
        
        df = user_analysis.find_teacher_users(
            db=db,
            course_ids=course_ids
        )
        
        return {
            'success': True,
            'count': len(df),
            'surveys': df.to_dict('records') if not df.empty else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding teacher surveys: {str(e)}")


@router.get("/survey_completion")
async def get_survey_completion_rates(
    course_ids: Optional[List[str]] = Query(None, description="Filter by course IDs"),
    db: Session = Depends(get_db)
):
    """
    Get survey completion rate analysis.
    
    Query Parameters:
        course_ids: Optional list of course IDs to analyze
        
    Returns:
        Survey completion statistics
    """
    try:
        from src.analysis import user_analysis
        
        df = user_analysis.analyze_survey_completion_rates(
            db=db,
            course_ids=course_ids
        )
        
        return {
            'success': True,
            'surveys': df.to_dict('records') if not df.empty else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing survey completion: {str(e)}")
