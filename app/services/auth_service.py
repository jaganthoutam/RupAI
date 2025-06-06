"""Authentication service using JWT."""

from datetime import datetime, timedelta
from typing import Any, Dict

import jwt
from passlib.hash import bcrypt

from ..models import User
from ..repositories.user_repository import UserRepository
from ..utils.crypto import encrypt_data
from ..config.settings import settings


class AuthService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def authenticate(self, email: str, password: str) -> str | None:
        user = await self.repo.get_by_email(email)
        if not user or not bcrypt.verify(password, user.hashed_password):
            return None
        payload: Dict[str, Any] = {
            "sub": user.id,
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")
        return token
