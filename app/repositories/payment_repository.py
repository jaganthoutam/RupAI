"""Payment repository accessing the database asynchronously."""

from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ..models import Payment


class PaymentRepository:
    """Repository for payments."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, payment: Payment) -> None:
        # Placeholder for SQL insertion using SQLAlchemy core/ORM
        await self.session.execute(text("SELECT 1"))

    async def get(self, payment_id: str) -> Payment | None:
        # Placeholder for SQL query
        await self.session.execute(text("SELECT 1"))
        return None

    async def list_by_user(self, user_id: str) -> Iterable[Payment]:
        await self.session.execute(text("SELECT 1"))
        return []
