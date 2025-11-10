"""
Database configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.core.config import settings

# Create database engine
_db_url = settings.database_url.get_secret_value() if settings.database_url else "sqlite:///./openhpi_automation.db"
engine = create_engine(
    _db_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if _db_url.startswith("sqlite") else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for getting database sessions.
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    """
    # Import tables to register models with Base
    from . import tables  # noqa: F401
    
    Base.metadata.create_all(bind=engine)
