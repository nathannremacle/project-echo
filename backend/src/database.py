"""
Database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.config import settings

# Create base class for models
Base = declarative_base()

# Create engine
# For SQLite, use StaticPool to allow multiple threads
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.APP_DEBUG,  # Log SQL queries in debug mode
    )
else:
    # PostgreSQL or other databases
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        echo=settings.APP_DEBUG,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency function to get database session
    Use this in FastAPI route dependencies
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database (create all tables)
    Should be called after Alembic migrations
    """
    Base.metadata.create_all(bind=engine)


def get_engine():
    """Get database engine (for Alembic)"""
    return engine
