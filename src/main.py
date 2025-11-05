"""
Main FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.models.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    init_db()
    print("✓ Database initialized")
    print(f"✓ Running in {settings.env} mode")
    yield
    # Shutdown (if needed in the future)


# Initialize FastAPI app
app = FastAPI(
    title="Data Pipeline Platform API",
    description="A modular platform for scraping, analyzing, and automating data pipelines. Supports multiple data sources including OpenHPI.",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "name": "Data Pipeline Platform API",
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.env,
        "docs_url": "/docs",
        "description": "Modular scraping and analysis platform supporting multiple data sources"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "environment": settings.env,
    }


# Import and include routers
from src.api import sources, data, courses, scraping, analysis, automation, ai

# Generic platform endpoints
app.include_router(sources.router, prefix="/api/sources", tags=["Sources"])
app.include_router(data.router, prefix="/api/data", tags=["Data"])

# OpenHPI-specific endpoints (legacy, now under "Example: OpenHPI")
app.include_router(courses.router, prefix="/api/courses", tags=["OpenHPI - Courses"])
app.include_router(scraping.router, prefix="/api/scraping", tags=["OpenHPI - Scraping"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["OpenHPI - Analysis"])
app.include_router(automation.router, prefix="/api/automation", tags=["OpenHPI - Automation"])
app.include_router(ai.router, prefix="/api/ai", tags=["OpenHPI - AI"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.api_workers,
    )
