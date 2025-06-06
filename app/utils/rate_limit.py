"""Simple in-memory rate limiting."""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import DefaultDict

from fastapi import HTTPException, Request

RATE_LIMIT_BUCKETS: DefaultDict[str, list[datetime]] = defaultdict(list)


def enforce_rate_limit(key: str, limit: int, period: timedelta) -> None:
    now = datetime.utcnow()
    window_start = now - period
    events = [t for t in RATE_LIMIT_BUCKETS[key] if t > window_start]
    RATE_LIMIT_BUCKETS[key] = events
    if len(events) >= limit:
        raise HTTPException(status_code=429, detail="rate limit exceeded")
    events.append(now)


async def rate_limit_dependency(request: Request) -> None:
    user = request.state.user_id if hasattr(request.state, "user_id") else request.client.host
    enforce_rate_limit(user, 1000, timedelta(hours=1))
