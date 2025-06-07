"""MCP tool context for dependency injection."""

from typing import Any, Dict, Optional
from dataclasses import dataclass

from ..services.payment_service import PaymentService
from ..services.wallet_service import WalletService
from ..services.analytics_service import AnalyticsService
from ..services.monitoring_service import MonitoringService
from ..services.audit_service import AuditService
from ..services.compliance_service import ComplianceService


@dataclass
class ToolContext:
    """Context object passed to MCP tools containing all required services."""
    
    payment_service: Optional[PaymentService]
    wallet_service: Optional[WalletService]
    analytics_service: Optional[AnalyticsService]
    monitoring_service: Optional[MonitoringService]
    audit_service: Optional[AuditService]
    compliance_service: Optional[ComplianceService]
    
    # Request context
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    request_metadata: Optional[Dict[str, Any]] = None 