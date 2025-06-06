"""Database model for payments."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class Payment(BaseModel):
    """Represents a payment transaction."""

    id: str = Field(..., description="Payment identifier")
    amount: Decimal = Field(..., ge=0)
    currency: str
    status: str
    customer_id: str
    provider: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Payment(BaseModel):
    id: str
    amount: Decimal
    currency: str
    status: str
