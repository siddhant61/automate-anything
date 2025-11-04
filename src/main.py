"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.models.database import init_db

# Initialize FastAPI app
app = FastAPI(
    title="OpenHPI Automation API",
    description="A unified API for OpenHPI course management, analytics, and automation",
    version="0.1.0",
    debug=settings.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print("✓ Database initialized")
    print(f"✓ Running in {settings.env} mode")


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
from src.api import courses, scraping

app.include_router(courses.router, prefix="/api/courses", tags=["Courses"])
app.include_router(scraping.router, prefix="/api/scraping", tags=["Scraping"])

# Additional routers will be added in future phases:
# from src.api import users, analytics, automation
# app.include_router(users.router, prefix="/api/users", tags=["Users"])
# app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
# app.include_router(automation.router, prefix="/api/automation", tags=["Automation"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.api_workers,
    )
