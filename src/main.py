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
    title="OpenHPI Automation API",
    description="A unified API for OpenHPI course management, analytics, and automation",
    version="0.1.0",
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
        "name": "OpenHPI Automation API",
        "version": "0.1.0",
        "status": "operational",
        "environment": settings.env,
        "docs_url": "/docs",
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
from src.api import courses, scraping, analysis, automation

app.include_router(courses.router, prefix="/api/courses", tags=["Courses"])
app.include_router(scraping.router, prefix="/api/scraping", tags=["Scraping"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(automation.router, prefix="/api/automation", tags=["Automation"])

# Additional routers will be added in future phases:
# from src.api import users
# app.include_router(users.router, prefix="/api/users", tags=["Users"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.api_workers,
    )
