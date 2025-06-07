"""
Database Session Management
Provides database session dependencies for FastAPI routes.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

# Global database instance - will be set by main.py
database = None


def set_database(db_instance):
    """Set the global database instance."""
    global database
    database = db_instance


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get database session.
    
    Yields:
        AsyncSession: Database session
    """
    if database is None:
        raise RuntimeError("Database not initialized. Call set_database() first.")
    
    async with database.get_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_sync() -> AsyncSession:
    """
    Get database session for non-FastAPI usage.
    
    Returns:
        AsyncSession: Database session
    """
    if database is None:
        raise RuntimeError("Database not initialized. Call set_database() first.")
    
    return database.get_session()


def async_session_factory():
    """
    Factory function to create async database sessions for Celery tasks.
    
    Returns:
        AsyncSession factory function
    """
    if database is None:
        raise RuntimeError("Database not initialized. Call set_database() first.")
    
    return database.get_session


def get_session():
    """
    Get database session factory for celery tasks.
    
    Returns:
        Database session factory
    """
    return async_session_factory() 