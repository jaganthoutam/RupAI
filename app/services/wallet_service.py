"""Wallet management service."""

from decimal import Decimal
from typing import Any, Dict

from ..models import Wallet
from ..repositories.wallet_repository import WalletRepository


class WalletService:
    def __init__(self, repo: WalletRepository) -> None:
        self.repo = repo

    async def get_balance(self, wallet_id: str) -> Wallet | None:
        return await self.repo.get(wallet_id)

    async def transfer_funds(self, wallet_id: str, target_wallet: str, amount: Decimal) -> None:
        await self.repo.update_balance(wallet_id, -float(amount))
        await self.repo.update_balance(target_wallet, float(amount))

    async def top_up(self, wallet_id: str, amount: Decimal) -> None:
        await self.repo.update_balance(wallet_id, float(amount))
