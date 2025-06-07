"""Service layer exports."""

from .payment_service import PaymentService
from .wallet_service import WalletService
from .auth_service import AuthService
from .audit_service import AuditService
from .analytics_service import AnalyticsService
from .monitoring_service import MonitoringService
from .compliance_service import ComplianceService

__all__ = [
    "PaymentService",
    "WalletService",
    "AuthService",
    "AuditService",
    "AnalyticsService",
    "MonitoringService",
    "ComplianceService"
]

"""Services module for MCP Payments Server."""

"""
Service dependency injection for FastAPI endpoints.

Provides service instances with proper dependency injection
for all business logic services.
"""

from typing import AsyncGenerator
from fastapi import Depends

from app.services.analytics_service import AnalyticsService
from app.services.payment_service import PaymentService
from app.services.wallet_service import WalletService
from app.services.monitoring_service import MonitoringService
from app.services.compliance_service import ComplianceService
from app.db.dependencies import get_database


# Service dependency functions
def get_analytics_service() -> AnalyticsService:
    """Get analytics service instance."""
    return AnalyticsService()


def get_payment_service() -> PaymentService:
    """Get payment service instance."""
    return PaymentService()


def get_wallet_service() -> WalletService:
    """Get wallet service instance."""
    return WalletService()


def get_monitoring_service() -> MonitoringService:
    """Get monitoring service instance."""
    return MonitoringService()


def get_compliance_service() -> ComplianceService:
    """Get compliance service instance."""
    return ComplianceService()


# Export service dependencies
AnalyticsService = Depends(get_analytics_service)
PaymentService = Depends(get_payment_service)
WalletService = Depends(get_wallet_service)
MonitoringService = Depends(get_monitoring_service)
ComplianceService = Depends(get_compliance_service)
