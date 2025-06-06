"""User repository."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ..models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        await self.session.execute(text("SELECT 1"))
        return None
