"""
API endpoints package for Enterprise MCP Payments Server.

This package contains all REST API endpoints including:
- Analytics endpoints (revenue, payments, users, fraud)
- Payment management endpoints
- Wallet management endpoints  
- System monitoring endpoints
- AI-powered insights endpoints
"""

from .analytics import router as analytics_router
from .payments import router as payments_router
from .wallets import router as wallets_router
from .monitoring import router as monitoring_router
from .compliance import router as compliance_router

__all__ = [
    "analytics_router",
    "payments_router", 
    "wallets_router",
    "monitoring_router",
    "compliance_router"
] 