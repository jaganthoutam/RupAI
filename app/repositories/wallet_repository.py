"""Wallet repository."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ..models import Wallet


class WalletRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, wallet_id: str) -> Wallet | None:
        await self.session.execute(text("SELECT 1"))
        return None

    async def update_balance(self, wallet_id: str, amount: float) -> None:
        await self.session.execute(text("SELECT 1"))
