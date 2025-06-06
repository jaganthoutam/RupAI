"""Payment-related MCP tools."""

from decimal import Decimal
from uuid import UUID
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from ..server import ToolContext
from ...services.payment_service import PaymentService


class CreatePaymentInput(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: str
    method: str
    customer_id: UUID
    idempotency_key: str
    metadata: Dict[str, Any] | None = None


async def create_payment(ctx: ToolContext, params: CreatePaymentInput) -> Dict[str, Any]:
    payment = await ctx.payment_service.create_payment(
        amount=params.amount,
        currency=params.currency,
        method=params.method,
        customer_id=params.customer_id,
        idempotency_key=params.idempotency_key,
        metadata=params.metadata,
    )
    return payment.model_dump()


class VerifyPaymentInput(BaseModel):
    payment_id: str


async def verify_payment(ctx: ToolContext, params: VerifyPaymentInput) -> Dict[str, Any]:
    payment = await ctx.payment_service.verify_payment(params.payment_id)
    return payment.model_dump() if payment else {}


class RefundPaymentInput(BaseModel):
    payment_id: str
    amount: Decimal


async def refund_payment(ctx: ToolContext, params: RefundPaymentInput) -> Dict[str, Any]:
    # Placeholder for refund logic
    return {"status": "refunded", "payment_id": params.payment_id}


class GetPaymentStatusInput(BaseModel):
    payment_id: str


async def get_payment_status(ctx: ToolContext, params: GetPaymentStatusInput) -> Dict[str, Any]:
    payment = await ctx.payment_service.verify_payment(params.payment_id)
    return {"status": payment.status if payment else "unknown"}
