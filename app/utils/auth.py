"""JWT authentication utilities."""

from typing import Optional

import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..config.settings import settings


class JWTBearer(HTTPBearer):
    """JWT auth dependency for FastAPI."""

    async def __call__(self, request: Request) -> Optional[str]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        token = credentials.credentials
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
            return payload.get("sub")
        except jwt.PyJWTError as exc:
            raise HTTPException(status_code=403, detail="invalid token") from exc
