"""
Enterprise MCP Payments Server - Main Entry Point
Model Context Protocol v2024.1 Implementation

Production-ready MCP server for payments processing with enterprise-grade
reliability, security, and observability.
"""

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.config.settings import settings
from app.config.logging import setup_logging
from app.mcp.server import MCPServer
from app.utils.monitoring import MetricsCollector
from app.utils.rate_limiting import RateLimiter
from app.middleware.auth import AuthMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.db.database import Database
from app.db.redis import RedisClient
from app.services.notification_service import NotificationService
from app.auth.routes import router as auth_router
from app.db.session import set_database

# Import all new API routers
from app.api.analytics import router as analytics_router
from app.api.payments import router as payments_router
from app.api.wallets import router as wallets_router
from app.api.monitoring import router as monitoring_router
from app.api.compliance import router as compliance_router
from app.api.config import router as config_router
from app.api.users import router as users_router
from app.api.subscriptions import router as subscriptions_router
from app.api.settings import router as settings_router
from app.api.advanced import router as advanced_router

# Import WebSocket router
from app.websockets import websocket_router

# Global instances
mcp_server: MCPServer = None
database: Database = None
redis_client: RedisClient = None
metrics_collector: MetricsCollector = None
notification_service: NotificationService = None

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management with proper startup and shutdown."""
    global mcp_server, database, redis_client, metrics_collector, notification_service
    
    try:
        # Setup logging
        setup_logging()
        logger.info("🚀 Starting Enterprise MCP Payments Server v%s", settings.SERVER_VERSION)
        
        # Initialize database
        database = Database()
        await database.connect()
        
        # Set the global database instance for session management
        set_database(database)
        
        logger.info("✅ Database connected")
        
        # Initialize Redis
        redis_client = RedisClient()
        await redis_client.connect()
        logger.info("✅ Redis connected")
        
        # Initialize metrics collector
        metrics_collector = MetricsCollector()
        await metrics_collector.initialize()
        logger.info("✅ Metrics collector initialized")
        
        # Initialize notification service
        notification_service = NotificationService()
        await notification_service.initialize()
        logger.info("✅ Notification service initialized")
        
        # Initialize MCP Server
        mcp_server = MCPServer(
            database=database,
            redis_client=redis_client,
            metrics_collector=metrics_collector,
            notification_service=notification_service
        )
        await mcp_server.initialize()
        logger.info("✅ MCP Server initialized")
        
        # Setup signal handlers
        setup_signal_handlers()
        
        logger.info("🎉 Enterprise MCP Payments Server started successfully")
        
        yield
        
    except Exception as e:
        logger.error("❌ Failed to start server: %s", str(e))
        raise
    finally:
        # Cleanup
        logger.info("🛑 Shutting down Enterprise MCP Payments Server...")
        
        if mcp_server:
            await mcp_server.shutdown()
            logger.info("✅ MCP Server shut down")
        
        if notification_service:
            await notification_service.shutdown()
            logger.info("✅ Notification service shut down")
            
        if metrics_collector:
            await metrics_collector.shutdown()
            logger.info("✅ Metrics collector shut down")
        
        if redis_client:
            await redis_client.disconnect()
            logger.info("✅ Redis disconnected")
        
        if database:
            await database.disconnect()
            logger.info("✅ Database disconnected")
        
        logger.info("👋 Enterprise MCP Payments Server shut down gracefully")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application with enterprise features."""
    
    app = FastAPI(
        title="Enterprise MCP Payments Server",
        description="Production-ready Model Context Protocol server for payments processing",
        version=settings.SERVER_VERSION,
        docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
        lifespan=lifespan,
        openapi_tags=[
            {
                "name": "MCP",
                "description": "Model Context Protocol operations",
            },
            {
                "name": "Health",
                "description": "Health check and monitoring endpoints",
            },
            {
                "name": "Payments",
                "description": "Payment processing operations",
            },
            {
                "name": "Wallets",
                "description": "Wallet management operations",
            },
        ]
    )
    
    # Add middleware
    setup_middleware(app)
    
    # Add routes
    setup_routes(app)
    
    # Setup metrics
    if settings.ENABLE_METRICS:
        instrumentator = Instrumentator()
        instrumentator.instrument(app).expose(app, endpoint="/metrics")
    
    return app


def setup_middleware(app: FastAPI) -> None:
    """Setup middleware stack with security and monitoring."""
    
    # Request ID middleware (first)
    app.add_middleware(RequestIDMiddleware)
    
    # Security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Authentication middleware
    if settings.ENABLE_AUTHENTICATION:
        app.add_middleware(AuthMiddleware)
    
    # Rate limiting middleware
    if settings.ENABLE_RATE_LIMITING:
        rate_limiter = RateLimiter()
        app.middleware("http")(rate_limiter.middleware)
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Gzip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)


def setup_routes(app: FastAPI) -> None:
    """Setup API routes and endpoints."""
    
    # Include API routers
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(analytics_router, prefix="/api/v1")
    app.include_router(payments_router, prefix="/api/v1")
    app.include_router(wallets_router, prefix="/api/v1")
    app.include_router(monitoring_router, prefix="/api/v1")
    app.include_router(compliance_router, prefix="/api/v1")
    app.include_router(config_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(subscriptions_router, prefix="/api/v1")
    app.include_router(settings_router, prefix="/api/v1")
    app.include_router(advanced_router, prefix="/api/v1")
    
    # Include WebSocket router
    app.include_router(websocket_router)
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "enterprise-mcp-payments",
            "version": settings.SERVER_VERSION,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    @app.get("/ready", tags=["Health"])
    async def readiness_check():
        """Readiness check endpoint."""
        checks = {}
        
        # Check database
        try:
            await database.health_check()
            checks["database"] = "healthy"
        except Exception as e:
            checks["database"] = f"unhealthy: {str(e)}"
        
        # Check Redis
        try:
            await redis_client.health_check()
            checks["redis"] = "healthy"
        except Exception as e:
            checks["redis"] = f"unhealthy: {str(e)}"
        
        # Check MCP server
        try:
            await mcp_server.health_check()
            checks["mcp_server"] = "healthy"
        except Exception as e:
            checks["mcp_server"] = f"unhealthy: {str(e)}"
        
        all_healthy = all(status == "healthy" for status in checks.values())
        
        return JSONResponse(
            status_code=200 if all_healthy else 503,
            content={
                "status": "ready" if all_healthy else "not_ready",
                "checks": checks,
                "timestamp": asyncio.get_event_loop().time()
            }
        )
    
    @app.post("/mcp", tags=["MCP"])
    async def mcp_handler(request: Request):
        """Main MCP protocol handler endpoint."""
        try:
            body = await request.json()
            response = await mcp_server.handle_request(body)
            return JSONResponse(content=response)
        except Exception as e:
            logger.error("MCP request handling error: %s", str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,  # Internal error
                        "message": "Internal server error",
                        "data": str(e) if settings.ENVIRONMENT == "development" else None
                    },
                    "id": body.get("id") if 'body' in locals() else None
                }
            )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler with proper logging."""
        logger.error(
            "Unhandled exception: %s | Path: %s | Method: %s",
            str(exc),
            request.url.path,
            request.method,
            exc_info=True
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": str(exc) if settings.ENVIRONMENT == "development" else "An error occurred"
            }
        )


def setup_signal_handlers() -> None:
    """Setup graceful shutdown signal handlers."""
    
    def signal_handler(signum, frame):
        logger.info("Received signal %s, initiating graceful shutdown...", signum)
        # Let the lifespan context manager handle the shutdown
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


# Create the application instance
app = create_app()

if __name__ == "__main__":
    """Run the server directly for development."""
    
    # Setup logging for direct run
    setup_logging()
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        server_header=False,  # Security: don't expose server info
        date_header=False,    # Security: don't expose date info
    )
