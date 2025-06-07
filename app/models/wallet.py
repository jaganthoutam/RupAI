"""Wallet model."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TransactionType(str, Enum):
    """Wallet transaction type enumeration."""
    CREDIT = "credit"
    DEBIT = "debit"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    REFUND = "refund"
    FEE = "fee"


class Wallet(BaseModel):
    """Represents a user's wallet."""

    id: str = Field(..., description="Wallet ID")
    user_id: str = Field(..., description="User ID")
    balance: Decimal = Field(default=Decimal("0"), description="Current balance")
    currency: str = Field(..., description="Currency code")
    is_active: bool = Field(default=True, description="Whether wallet is active")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class WalletTransaction(BaseModel):
    """Represents a wallet transaction."""
    
    model_config = ConfigDict(use_enum_values=True)
    
    id: str = Field(..., description="Transaction ID")
    wallet_id: str = Field(..., description="Wallet ID")
    transaction_type: TransactionType = Field(..., description="Transaction type")
    amount: Decimal = Field(..., description="Transaction amount")
    balance_before: Decimal = Field(..., description="Balance before transaction")
    balance_after: Decimal = Field(..., description="Balance after transaction")
    reference_id: Optional[str] = Field(None, description="Reference transaction ID")
    description: Optional[str] = Field(None, description="Transaction description")
    metadata: Optional[dict] = Field(None, description="Additional metadata")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
