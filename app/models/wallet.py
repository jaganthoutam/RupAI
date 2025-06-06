"""Wallet model."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class Wallet(BaseModel):
    """Represents a user's wallet."""

    id: str = Field(..., description="Wallet ID")
    user_id: str
    balance: Decimal = Field(default=Decimal("0"))
    currency: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
