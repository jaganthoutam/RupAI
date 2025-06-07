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
from app.services.simple_monitoring_service import SimpleMonitoringService
from app.services.compliance_service import ComplianceService
from app.db.dependencies import get_database


class MockAuditRepository:
    """Mock audit repository for development."""
    async def create_audit_log(self, *args, **kwargs): return None
    async def get_audit_logs(self, *args, **kwargs): return []


class MockCacheManager:
    """Mock cache manager for development."""
    async def get(self, key): return None
    async def set(self, key, value, ttl=None): return None


class MockMetricsCollector:
    """Mock metrics collector for development."""
    def increment_counter(self, name): pass
    def record_histogram(self, name, value): pass


class MockNotificationManager:
    """Mock notification manager for development."""
    async def send_notification(self, *args, **kwargs): pass


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


def get_monitoring_service() -> SimpleMonitoringService:
    """Get monitoring service instance with minimal dependencies."""
    # Use the simple constructor for API endpoints
    return SimpleMonitoringService()


def get_compliance_service() -> ComplianceService:
    """Get compliance service instance with mock dependencies."""
    return ComplianceService(audit_repository=MockAuditRepository())


# All dependency functions are available for import
# Use get_*_service functions in your API endpoints
