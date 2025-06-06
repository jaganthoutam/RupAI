"""Simplified Stripe client."""

from typing import Any, Dict

import aiohttp

from ..models import Payment
from ..config.settings import settings


class StripeClient:
    """Interacts with Stripe APIs."""

    base_url = "https://api.stripe.com/v1"

    async def create_charge(self, payment: Payment, metadata: Dict[str, Any] | None = None) -> None:
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"{self.base_url}/charges",
                auth=aiohttp.BasicAuth(settings.stripe_api_key, ""),
                data={
                    "amount": int(payment.amount * 100),
                    "currency": payment.currency.lower(),
                    "metadata": metadata or {},
                },
            )
