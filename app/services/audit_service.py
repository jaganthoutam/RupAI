"""Audit logging service."""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

from ..models import AuditLog
from ..repositories.audit_repository import AuditRepository

logger = logging.getLogger(__name__)


class AuditService:
    def __init__(self, repo: AuditRepository) -> None:
        self.repo = repo
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize the audit service."""
        try:
            logger.info("🔄 Initializing audit service...")
            self.initialized = True
            logger.info("✅ Audit service initialized successfully")
        except Exception as e:
            logger.error("❌ Failed to initialize audit service: %s", str(e))
            raise

    async def shutdown(self) -> None:
        """Shutdown the audit service gracefully."""
        try:
            logger.info("🔄 Shutting down audit service...")
            self.initialized = False
            logger.info("✅ Audit service shut down successfully")
        except Exception as e:
            logger.error("❌ Error during audit service shutdown: %s", str(e))
            raise

    async def log(self, entry: AuditLog) -> None:
        """Log an audit entry."""
        await self.repo.add(entry)

    async def log_event(
        self,
        event_type: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Log an audit event with comprehensive context.
        
        Args:
            event_type: Type of event (e.g., 'mcp_server_initialized')
            session_id: Session identifier
            user_id: User identifier
            resource_id: Resource identifier
            metadata: Additional event metadata
            ip_address: Client IP address
            user_agent: Client user agent
        """
        try:
            audit_entry = AuditLog(
                id=str(uuid4()),
                timestamp=datetime.utcnow(),
                user_id=user_id,
                action=event_type,
                resource_id=resource_id,
                status="success",
                client_ip=ip_address,
                user_agent=user_agent,
                metadata={
                    "session_id": session_id,
                    **(metadata or {})
                }
            )
            
            await self.log(audit_entry)
            logger.debug("Audit event logged: %s", event_type)
            
        except Exception as e:
            logger.error("Failed to log audit event %s: %s", event_type, str(e))
            # Don't raise exception to avoid breaking the main flow
