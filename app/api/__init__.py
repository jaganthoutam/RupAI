"""
API endpoints package for Enterprise MCP Payments Server.

This package contains all REST API endpoints including:
- Analytics endpoints (revenue, payments, users, fraud)
- Payment management endpoints
- Wallet management endpoints  
- User management endpoints
- Subscription management endpoints
- Settings & configuration endpoints
- Advanced features endpoints (MCP tools, AI insights, reports, chat, docs)
- System monitoring endpoints
- AI-powered insights endpoints
"""

from .analytics import router as analytics_router
from .payments import router as payments_router
from .wallets import router as wallets_router
from .monitoring import router as monitoring_router
from .compliance import router as compliance_router
from .users import router as users_router
from .subscriptions import router as subscriptions_router
from .settings import router as settings_router
from .advanced import router as advanced_router

__all__ = [
    "analytics_router",
    "payments_router", 
    "wallets_router",
    "monitoring_router",
    "compliance_router",
    "users_router",
    "subscriptions_router",
    "settings_router",
    "advanced_router"
] 