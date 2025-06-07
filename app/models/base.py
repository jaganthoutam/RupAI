"""Base database configuration for all models."""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Shared base for all models
Base = declarative_base()

# Database session management (will be configured with actual URL later)
SessionLocal = sessionmaker(autocommit=False, autoflush=False)

def get_database_session():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 