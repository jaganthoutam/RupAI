"""Audit log repository."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ..models import AuditLog


class AuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, log: AuditLog) -> None:
        await self.session.execute(text("SELECT 1"))
