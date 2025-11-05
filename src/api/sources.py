"""
API endpoints for managing data sources.

Generic source management for the platform.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.models.tables import Source
from src.core.utils import utcnow

router = APIRouter()


class SourceCreate(BaseModel):
    """Request model for creating a source."""
    name: str
    url: str
    source_type: str
    module_name: str
    config: Optional[dict] = None
    is_active: bool = True


class SourceUpdate(BaseModel):
    """Request model for updating a source."""
    name: Optional[str] = None
    url: Optional[str] = None
    source_type: Optional[str] = None
    module_name: Optional[str] = None
    config: Optional[dict] = None
    is_active: Optional[bool] = None


@router.post("/")
async def create_source(
    source_data: SourceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new data source.
    
    Args:
        source_data: Source configuration
        
    Returns:
        Created source details
    """
    # Check if source with this name already exists
    existing = db.query(Source).filter_by(name=source_data.name).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Source with name '{source_data.name}' already exists"
        )
    
    # Create source
    source = Source(
        name=source_data.name,
        url=source_data.url,
        source_type=source_data.source_type,
        module_name=source_data.module_name,
        config=source_data.config,
        is_active=source_data.is_active
    )
    
    db.add(source)
    db.commit()
    db.refresh(source)
    
    return {
        'success': True,
        'message': 'Source created successfully',
        'source': {
            'id': source.id,
            'name': source.name,
            'url': source.url,
            'source_type': source.source_type,
            'module_name': source.module_name,
            'config': source.config,
            'is_active': source.is_active,
            'created_at': source.created_at.isoformat() if source.created_at else None,
        }
    }


@router.get("/")
async def list_sources(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    List all data sources with optional filtering.
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        source_type: Filter by source type
        is_active: Filter by active status
        
    Returns:
        List of sources
    """
    query = db.query(Source)
    
    # Apply filters
    if source_type:
        query = query.filter(Source.source_type == source_type)
    if is_active is not None:
        query = query.filter(Source.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    sources = query.offset(skip).limit(limit).all()
    
    return {
        'success': True,
        'total': total,
        'skip': skip,
        'limit': limit,
        'count': len(sources),
        'sources': [
            {
                'id': source.id,
                'name': source.name,
                'url': source.url,
                'source_type': source.source_type,
                'module_name': source.module_name,
                'is_active': source.is_active,
                'last_scraped_at': source.last_scraped_at.isoformat() if source.last_scraped_at else None,
                'created_at': source.created_at.isoformat() if source.created_at else None,
            }
            for source in sources
        ]
    }


@router.get("/{source_id}")
async def get_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific source.
    
    Args:
        source_id: Source identifier
        
    Returns:
        Source details
    """
    source = db.query(Source).filter_by(id=source_id).first()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    return {
        'success': True,
        'source': {
            'id': source.id,
            'name': source.name,
            'url': source.url,
            'source_type': source.source_type,
            'module_name': source.module_name,
            'config': source.config,
            'is_active': source.is_active,
            'last_scraped_at': source.last_scraped_at.isoformat() if source.last_scraped_at else None,
            'created_at': source.created_at.isoformat() if source.created_at else None,
            'updated_at': source.updated_at.isoformat() if source.updated_at else None,
        }
    }


@router.put("/{source_id}")
async def update_source(
    source_id: int,
    source_data: SourceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a source.
    
    Args:
        source_id: Source identifier
        source_data: Updated source data
        
    Returns:
        Updated source details
    """
    source = db.query(Source).filter_by(id=source_id).first()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Update fields
    if source_data.name is not None:
        source.name = source_data.name
    if source_data.url is not None:
        source.url = source_data.url
    if source_data.source_type is not None:
        source.source_type = source_data.source_type
    if source_data.module_name is not None:
        source.module_name = source_data.module_name
    if source_data.config is not None:
        source.config = source_data.config
    if source_data.is_active is not None:
        source.is_active = source_data.is_active
    
    source.updated_at = utcnow()
    
    db.commit()
    db.refresh(source)
    
    return {
        'success': True,
        'message': 'Source updated successfully',
        'source': {
            'id': source.id,
            'name': source.name,
            'url': source.url,
            'source_type': source.source_type,
            'module_name': source.module_name,
            'config': source.config,
            'is_active': source.is_active,
            'updated_at': source.updated_at.isoformat() if source.updated_at else None,
        }
    }


@router.delete("/{source_id}")
async def delete_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a source.
    
    Args:
        source_id: Source identifier
        
    Returns:
        Deletion confirmation
    """
    source = db.query(Source).filter_by(id=source_id).first()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    db.delete(source)
    db.commit()
    
    return {
        'success': True,
        'message': f'Source "{source.name}" deleted successfully'
    }
