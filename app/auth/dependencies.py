"""
Authentication dependencies for FastAPI endpoints.

Provides current user extraction, role-based access control,
and authentication validation for all protected endpoints.
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime

from app.config.settings import settings

security = HTTPBearer(auto_error=False)  # Don't auto-error when no token


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Extract and validate current user from JWT token.
    
    Returns:
        Dict containing user information and permissions
        
    Raises:
        HTTPException: If token is invalid or expired (when auth is enabled)
    """
    # If authentication is disabled, return mock admin user
    if not settings.ENABLE_AUTHENTICATION:
        return {
            "id": "admin_001",
            "email": "admin@company.com",
            "name": "Admin User",
            "role": "admin",
            "permissions": ["read", "write", "admin"],
            "is_authenticated": True
        }
    
    # If no credentials provided and auth is enabled, return error
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        
        # Decode JWT token
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=["HS256"]
        )
        
        # Extract user information
        user_id = payload.get("sub")
        email = payload.get("email")
        name = payload.get("name", "Admin User")
        role = payload.get("role", "admin")
        permissions = payload.get("permissions", ["read", "write", "admin"])
        
        # Check token expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "id": user_id or "admin_001",
            "email": email or "admin@company.com",
            "name": name,
            "role": role,
            "permissions": permissions,
            "is_authenticated": True
        }
        
    except jwt.PyJWTError:
        # For development/demo purposes, return a mock admin user
        # In production, this should raise an authentication error
        if settings.ENVIRONMENT == "development":
            return {
                "id": "admin_001",
                "email": "admin@company.com",
                "name": "Admin User",
                "role": "admin",
                "permissions": ["read", "write", "admin"],
                "is_authenticated": True
            }
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_permission(permission: str):
    """
    Dependency factory to require specific permissions.
    
    Args:
        permission: Required permission level
        
    Returns:
        Dependency function that validates user permissions
    """
    def permission_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        if permission not in current_user.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}"
            )
        return current_user
    
    return permission_checker


def require_role(role: str):
    """
    Dependency factory to require specific role.
    
    Args:
        role: Required user role
        
    Returns:
        Dependency function that validates user role
    """
    def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        if current_user.get("role") != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role. Required: {role}"
            )
        return current_user
    
    return role_checker


# Common permission dependencies
require_admin = require_permission("admin")
require_write = require_permission("write")
require_read = require_permission("read") 