"""Simplified Razorpay client."""

from typing import Any, Dict

import aiohttp

from ..models import Payment
from ..config.settings import settings


class RazorpayClient:
    """Interacts with Razorpay APIs."""

    base_url = "https://api.razorpay.com/v1"

    async def create_payment(self, payment: Payment, metadata: Dict[str, Any] | None = None) -> None:
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"{self.base_url}/payments",
                auth=aiohttp.BasicAuth(settings.razorpay_key_id, settings.razorpay_key_secret),
                json={
                    "amount": int(payment.amount * 100),
                    "currency": payment.currency,
                    "notes": metadata or {},
                },
            )
