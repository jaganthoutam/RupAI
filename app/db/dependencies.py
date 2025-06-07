"""
Database dependencies for FastAPI endpoints.

Provides database session management and dependency injection
for all endpoints requiring database access.
"""

from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to provide database session for endpoints.
    
    Yields:
        AsyncSession: Database session for the request
    """
    async for session in get_db():
        yield session 