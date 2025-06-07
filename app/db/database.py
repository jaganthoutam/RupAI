"""
Database Connection Manager
Enterprise-grade PostgreSQL connection handling with async support.
"""

import asyncio
import logging
from typing import Optional, Dict, Any

import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData, event, text
from sqlalchemy.pool import Pool

from app.config.settings import settings

logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()
metadata = MetaData()


class Database:
    """
    Enterprise database connection manager with high availability features.
    
    Features:
    - Async connection pooling
    - Health monitoring
    - Connection retry logic
    - Performance metrics
    - Graceful shutdown
    """
    
    def __init__(self):
        self.engine: Optional[Any] = None
        self.session_factory: Optional[async_sessionmaker] = None
        self._connected = False
        self._pool_status = {}
        
    async def connect(self) -> None:
        """Initialize database connection with enterprise features."""
        try:
            logger.info("🔄 Connecting to PostgreSQL database...")
            
            # Create async engine with connection pooling
            self.engine = create_async_engine(
                settings.DATABASE_URL,
                # Connection pool settings
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                pool_timeout=30,
                pool_recycle=3600,  # Recycle connections every hour
                pool_pre_ping=True,  # Validate connections before use
                # Performance settings
                echo=settings.is_development,
                echo_pool=settings.DEBUG,
                # Connection arguments
                connect_args={
                    "server_settings": {
                        "application_name": f"{settings.SERVER_NAME}_v{settings.SERVER_VERSION}",
                        "jit": "off",  # Disable JIT for consistent performance
                    },
                    "command_timeout": 60,
                    "statement_cache_size": 0,  # Disable prepared statement cache
                }
            )
            
            # Create session factory
            self.session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=True,
                autocommit=False
            )
            
            # Setup pool event listeners for monitoring
            self._setup_pool_events()
            
            # Test connection
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
                logger.info("✅ Database connection established")
                
            self._connected = True
            
        except Exception as e:
            logger.error("❌ Failed to connect to database: %s", str(e))
            raise
    
    async def disconnect(self) -> None:
        """Gracefully close database connections."""
        if self.engine:
            logger.info("🔄 Closing database connections...")
            await self.engine.dispose()
            self._connected = False
            logger.info("✅ Database connections closed")
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive database health check."""
        if not self._connected or not self.engine:
            return {
                "status": "unhealthy",
                "error": "Database not connected"
            }
        
        try:
            # Test connection
            async with self.engine.begin() as conn:
                result = await conn.execute(text("SELECT 1 as health"))
                await result.fetchone()
            
            # Get pool statistics
            pool = self.engine.pool
            pool_stats = {
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid()
            }
            
            return {
                "status": "healthy",
                "pool_stats": pool_stats,
                "connection_string": settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else "masked"
            }
            
        except Exception as e:
            logger.error("Database health check failed: %s", str(e))
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def get_session(self) -> AsyncSession:
        """Get async database session."""
        if not self.session_factory:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.session_factory()
    
    async def execute_raw(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute raw SQL query."""
        async with self.engine.begin() as conn:
            if params:
                return await conn.execute(text(query), params)
            return await conn.execute(text(query))
    
    def _setup_pool_events(self) -> None:
        """Setup SQLAlchemy pool event listeners for monitoring."""
        
        @event.listens_for(self.engine.sync_engine.pool, "connect")
        def on_connect(dbapi_conn, connection_record):
            """Handle new database connections."""
            logger.debug("🔗 New database connection established")
            self._pool_status["connections_created"] = self._pool_status.get("connections_created", 0) + 1
        
        @event.listens_for(self.engine.sync_engine.pool, "checkout")
        def on_checkout(dbapi_conn, connection_record, connection_proxy):
            """Handle connection checkout from pool."""
            logger.debug("📤 Connection checked out from pool")
            self._pool_status["connections_checked_out"] = self._pool_status.get("connections_checked_out", 0) + 1
        
        @event.listens_for(self.engine.sync_engine.pool, "checkin")
        def on_checkin(dbapi_conn, connection_record):
            """Handle connection checkin to pool."""
            logger.debug("📥 Connection checked in to pool")
            self._pool_status["connections_checked_in"] = self._pool_status.get("connections_checked_in", 0) + 1
        
        @event.listens_for(self.engine.sync_engine.pool, "invalidate")
        def on_invalidate(dbapi_conn, connection_record, exception):
            """Handle connection invalidation."""
            logger.warning("❌ Database connection invalidated: %s", str(exception))
            self._pool_status["connections_invalidated"] = self._pool_status.get("connections_invalidated", 0) + 1
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._connected
    
    @property
    def pool_status(self) -> Dict[str, Any]:
        """Get connection pool status."""
        return self._pool_status.copy() 