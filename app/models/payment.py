"""Database model for payments."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    """Payment method enumeration."""
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"
    UPI = "upi"
    CRYPTO = "crypto"


class Payment(BaseModel):
    """Represents a payment transaction."""

    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(..., description="Payment identifier")
    amount: Decimal = Field(..., ge=0, description="Payment amount")
    currency: str = Field(..., description="Currency code (ISO 4217)")
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Payment status")
    method: PaymentMethod = Field(..., description="Payment method")
    customer_id: str = Field(..., description="Customer identifier")
    provider: str = Field(..., description="Payment provider")
    provider_transaction_id: Optional[str] = Field(None, description="Provider transaction ID")
    description: Optional[str] = Field(None, description="Payment description")
    metadata: Optional[dict] = Field(None, description="Additional metadata")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
