"""User model."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    OPERATOR = "operator"
    ANALYST = "analyst"
    USER = "user"
    GUEST = "guest"


class User(BaseModel):
    """Represents an application user."""

    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    hashed_password: str = Field(..., description="Hashed password")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    is_active: bool = Field(default=True, description="Whether user is active")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
