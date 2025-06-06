"""Payment business service with Stripe and Razorpay integration."""

from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID

from ..models import Payment
from ..repositories.payment_repository import PaymentRepository
from ..integrations.stripe_client import StripeClient
from ..integrations.razorpay_client import RazorpayClient
from ..utils.crypto import encrypt_data


class PaymentService:
    """Handles payment workflows."""

    def __init__(self, repo: PaymentRepository, stripe: StripeClient, razorpay: RazorpayClient) -> None:
        self.repo = repo
        self.stripe = stripe
        self.razorpay = razorpay

    async def create_payment(
        self,
        amount: Decimal,
        currency: str,
        method: str,
        customer_id: UUID,
        idempotency_key: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Payment:
        # Simplified provider selection
        provider = "stripe" if method == "card" else "razorpay"
        payment = Payment(
            id=idempotency_key,
            amount=amount,
            currency=currency,
            status="pending",
            customer_id=str(customer_id),
            provider=provider,
        )
        await self.repo.add(payment)
        if provider == "stripe":
            await self.stripe.create_charge(payment, metadata)
        else:
            await self.razorpay.create_payment(payment, metadata)
        return payment

    async def verify_payment(self, payment_id: str) -> Payment | None:
        return await self.repo.get(payment_id)
