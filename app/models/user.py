"""User model."""

from datetime import datetime

from pydantic import BaseModel, Field


class User(BaseModel):
    """Represents an application user."""

    id: str = Field(..., description="User ID")
    email: str
    hashed_password: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
