"""Wallet-related MCP tools."""

from decimal import Decimal
from uuid import UUID
from typing import Any, Dict

from pydantic import BaseModel, Field

from ..server import ToolContext


class GetWalletBalanceInput(BaseModel):
    wallet_id: str


async def get_wallet_balance(ctx: ToolContext, params: GetWalletBalanceInput) -> Dict[str, Any]:
    wallet = await ctx.wallet_service.get_balance(params.wallet_id)
    return wallet.model_dump() if wallet else {}


class TransferFundsInput(BaseModel):
    source_wallet: str
    target_wallet: str
    amount: Decimal = Field(..., gt=0)


async def transfer_funds(ctx: ToolContext, params: TransferFundsInput) -> Dict[str, Any]:
    await ctx.wallet_service.transfer_funds(params.source_wallet, params.target_wallet, params.amount)
    return {"status": "success"}


class WalletHistoryInput(BaseModel):
    wallet_id: str


async def wallet_transaction_history(ctx: ToolContext, params: WalletHistoryInput) -> Dict[str, Any]:
    return {"history": []}


class TopUpWalletInput(BaseModel):
    wallet_id: str
    amount: Decimal = Field(..., gt=0)


async def top_up_wallet(ctx: ToolContext, params: TopUpWalletInput) -> Dict[str, Any]:
    await ctx.wallet_service.top_up(params.wallet_id, params.amount)
    return {"status": "topped_up"}
