"""MCP tool registry."""

from .payments import (
    create_payment,
    verify_payment,
    refund_payment,
    get_payment_status,
)
from .wallets import (
    get_wallet_balance,
    transfer_funds,
    wallet_transaction_history,
    top_up_wallet,
)

TOOL_REGISTRY = {
    "create_payment": create_payment,
    "verify_payment": verify_payment,
    "refund_payment": refund_payment,
    "get_payment_status": get_payment_status,
    "get_wallet_balance": get_wallet_balance,
    "transfer_funds": transfer_funds,
    "wallet_transaction_history": wallet_transaction_history,
    "top_up_wallet": top_up_wallet,
}

__all__ = ["TOOL_REGISTRY"]
