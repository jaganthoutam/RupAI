"""Audit log entry model."""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field


class AuditLog(BaseModel):
    """Represents an immutable audit log entry."""

    id: str = Field(..., description="Audit entry ID")
    timestamp: datetime
    user_id: str | None = None
    action: str
    resource_id: str | None = None
    status: str
    client_ip: str | None = None
    user_agent: str | None = None
    metadata: Dict[str, Any] | None = None
