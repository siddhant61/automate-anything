"""
API endpoints for generic data access.

Access scraped and processed data from any source.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.models.tables import Source, ScrapedData, ProcessedData
from src.services.scraping_orchestrator import scraping_orchestrator

router = APIRouter()


@router.post("/scrape/{source_id}")
async def scrape_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    """
    Trigger a scrape for a specific source.
    
    Args:
        source_id: ID of the source to scrape
        
    Returns:
        Scraping results
    """
    try:
        result = scraping_orchestrator.scrape_source(db, source_id)
        return {
            'success': True,
            'message': f'Scraping completed for source {source_id}',
            'result': result
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@router.get("/scraped/{source_id}")
async def get_scraped_data(
    source_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get raw scraped data for a source.
    
    Args:
        source_id: ID of the source
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List of scraped data records
    """
    # Verify source exists
    source = db.query(Source).filter_by(id=source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Get scraped data
    query = db.query(ScrapedData).filter_by(source_id=source_id)
    total = query.count()
    
    scraped_items = query.order_by(
        ScrapedData.scraped_at.desc()
    ).offset(skip).limit(limit).all()
    
    return {
        'success': True,
        'source_id': source_id,
        'source_name': source.name,
        'total': total,
        'skip': skip,
        'limit': limit,
        'count': len(scraped_items),
        'scraped_data': [
            {
                'id': item.id,
                'url': item.url,
                'scraped_at': item.scraped_at.isoformat() if item.scraped_at else None,
                'status_code': item.status_code,
                'content_type': item.content_type,
                'has_html': bool(item.raw_html),
                'has_json': bool(item.raw_json),
                'has_text': bool(item.raw_text),
            }
            for item in scraped_items
        ]
    }


@router.get("/scraped/detail/{scraped_id}")
async def get_scraped_detail(
    scraped_id: int,
    include_raw: bool = Query(False, description="Include raw HTML/JSON content"),
    db: Session = Depends(get_db)
):
    """
    Get detailed scraped data including raw content.
    
    Args:
        scraped_id: ID of the scraped data
        include_raw: Whether to include raw HTML/JSON
        
    Returns:
        Detailed scraped data
    """
    scraped = db.query(ScrapedData).filter_by(id=scraped_id).first()
    if not scraped:
        raise HTTPException(status_code=404, detail="Scraped data not found")
    
    response = {
        'success': True,
        'scraped_data': {
            'id': scraped.id,
            'source_id': scraped.source_id,
            'url': scraped.url,
            'scraped_at': scraped.scraped_at.isoformat() if scraped.scraped_at else None,
            'status_code': scraped.status_code,
            'content_type': scraped.content_type,
        }
    }
    
    if include_raw:
        response['scraped_data']['raw_html'] = scraped.raw_html
        response['scraped_data']['raw_json'] = scraped.raw_json
        response['scraped_data']['raw_text'] = scraped.raw_text
    
    return response


@router.get("/processed/{source_id}")
async def get_processed_data(
    source_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get processed/analyzed data for a source.
    
    Args:
        source_id: ID of the source
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List of processed data records
    """
    # Verify source exists
    source = db.query(Source).filter_by(id=source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Get processed data through scraped_data relationship
    query = db.query(ProcessedData).join(
        ScrapedData, ProcessedData.scraped_data_id == ScrapedData.id
    ).filter(ScrapedData.source_id == source_id)
    
    total = query.count()
    
    processed_items = query.order_by(
        ProcessedData.processed_at.desc()
    ).offset(skip).limit(limit).all()
    
    return {
        'success': True,
        'source_id': source_id,
        'source_name': source.name,
        'total': total,
        'skip': skip,
        'limit': limit,
        'count': len(processed_items),
        'processed_data': [
            {
                'id': item.id,
                'title': item.title,
                'content_text': item.content_text[:200] + '...' if item.content_text and len(item.content_text) > 200 else item.content_text,
                'summary': item.summary,
                'sentiment_score': item.sentiment_score,
                'key_concepts': item.key_concepts,
                'metadata': item.data_metadata,
                'processor_module': item.processor_module,
                'processed_at': item.processed_at.isoformat() if item.processed_at else None,
            }
            for item in processed_items
        ]
    }


@router.get("/processed/detail/{processed_id}")
async def get_processed_detail(
    processed_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed processed data.
    
    Args:
        processed_id: ID of the processed data
        
    Returns:
        Detailed processed data
    """
    processed = db.query(ProcessedData).filter_by(id=processed_id).first()
    if not processed:
        raise HTTPException(status_code=404, detail="Processed data not found")
    
    return {
        'success': True,
        'processed_data': {
            'id': processed.id,
            'scraped_data_id': processed.scraped_data_id,
            'title': processed.title,
            'content_text': processed.content_text,
            'summary': processed.summary,
            'sentiment_score': processed.sentiment_score,
            'key_concepts': processed.key_concepts,
            'metadata': processed.data_metadata,
            'processor_module': processed.processor_module,
            'processed_at': processed.processed_at.isoformat() if processed.processed_at else None,
        }
    }


@router.get("/modules")
async def list_available_modules():
    """
    List all available scraping modules.
    
    Returns:
        List of registered modules
    """
    return {
        'success': True,
        'scrapers': scraping_orchestrator.list_available_scrapers()
    }
