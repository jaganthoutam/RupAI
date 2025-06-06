"""Audit logging service."""

from ..models import AuditLog
from ..repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, repo: AuditRepository) -> None:
        self.repo = repo

    async def log(self, entry: AuditLog) -> None:
        await self.repo.add(entry)
