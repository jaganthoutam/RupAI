"""Simplified main.py for testing configuration and basic functionality."""

import os
import logging
from fastapi import FastAPI

# Test environment variables first
print("🔧 Environment variables:")
print(f"JWT_SECRET_KEY: {os.getenv('JWT_SECRET_KEY', 'NOT_SET')}")
print(f"ENCRYPTION_KEY: {os.getenv('ENCRYPTION_KEY', 'NOT_SET')}")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT_SET')}")
print(f"REDIS_URL: {os.getenv('REDIS_URL', 'NOT_SET')}")

# Try to import settings
try:
    from app.config.settings import settings
    print(f"✅ Settings loaded successfully!")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Server host: {settings.HOST}")
    print(f"Server port: {settings.PORT}")
    print(f"Database URL: {settings.DATABASE_URL[:50]}...")
    print(f"Redis URL: {settings.REDIS_URL}")
except Exception as e:
    print(f"❌ Error loading settings: {e}")
    import traceback
    traceback.print_exc()

# Create a simple FastAPI app
app = FastAPI(
    title="Simple MCP Test Server",
    description="Basic test server for MCP Payments",
    version="1.0.0"
)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "mcp-payments-simple",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Hello from MCP Payments Server",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/test-config")
async def test_config():
    """Test configuration endpoint."""
    try:
        from app.config.settings import settings
        return {
            "status": "success",
            "environment": settings.ENVIRONMENT,
            "host": settings.HOST,
            "port": settings.PORT,
            "features": {
                "authentication": settings.ENABLE_AUTHENTICATION,
                "rate_limiting": settings.ENABLE_RATE_LIMITING,
                "metrics": settings.ENABLE_METRICS,
                "analytics": settings.ENABLE_ANALYTICS
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Simple MCP Payments Server...")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    ) 