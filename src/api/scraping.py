"""
API endpoints for scraping operations.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.services.scraping_service import scrape_courses, ScrapingError

router = APIRouter()


@router.post("/courses")
async def scrape_courses_endpoint(db: Session = Depends(get_db)):
    """
    Scrape course list from OpenHPI and save to database.
    
    This endpoint triggers the scraping job to fetch all available courses
    from the OpenHPI platform and persist them to the database.
    
    Returns:
        Dict: Scraping results including number of courses processed
    """
    try:
        result = scrape_courses(db)
        return {
            "success": True,
            "message": f"Successfully scraped and saved {result['courses_saved']} courses",
            "data": result
        }
    except ScrapingError as e:
        raise HTTPException(status_code=500, detail=f"Scraping error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/jobs")
async def list_scraping_jobs(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    List recent scraping jobs.
    
    Args:
        limit: Maximum number of jobs to return (default 10)
        
    Returns:
        List of scraping jobs with their status
    """
    from src.models.tables import ScrapingJob
    
    jobs = db.query(ScrapingJob)\
        .order_by(ScrapingJob.started_at.desc())\
        .limit(limit)\
        .all()
    
    return {
        "success": True,
        "count": len(jobs),
        "jobs": [
            {
                "id": job.id,
                "type": job.job_type,
                "status": job.status,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "records_processed": job.records_processed,
                "error": job.error_message
            }
            for job in jobs
        ]
    }


@router.get("/jobs/{job_id}")
async def get_scraping_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific scraping job.
    
    Args:
        job_id: ID of the scraping job
        
    Returns:
        Job details
    """
    from src.models.tables import ScrapingJob
    
    job = db.query(ScrapingJob).filter_by(id=job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "success": True,
        "job": {
            "id": job.id,
            "type": job.job_type,
            "status": job.status,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "records_processed": job.records_processed,
            "error": job.error_message,
            "metadata": job.job_metadata
        }
    }
