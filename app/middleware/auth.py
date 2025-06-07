"""
Authentication Middleware
JWT-based authentication middleware for secure API access.
"""

import logging
from typing import Optional

from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import jwt

from app.config.settings import settings

logger = logging.getLogger(__name__)

security = HTTPBearer()


class AuthMiddleware(BaseHTTPMiddleware):
    """
    JWT Authentication Middleware.
    
    Validates JWT tokens for protected endpoints and adds user context
    to the request state.
    """
    
    # Endpoints that don't require authentication
    EXEMPT_PATHS = {
        "/health",
        "/ready",
        "/metrics",
        "/docs",
        "/redoc",
        "/openapi.json"
    }
    
    async def dispatch(self, request: Request, call_next):
        """Process request with authentication check."""
        
        # Skip authentication for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        
        # Skip authentication if disabled
        if not settings.ENABLE_AUTHENTICATION:
            return await call_next(request)
        
        try:
            # Extract and validate JWT token
            token = self._extract_token(request)
            if token:
                user_data = self._validate_token(token)
                request.state.user = user_data
                request.state.authenticated = True
            else:
                request.state.user = None
                request.state.authenticated = False
                
                # Return 401 for protected endpoints
                if self._is_protected_endpoint(request.url.path):
                    return Response(
                        content='{"error": "Authentication required"}',
                        status_code=401,
                        media_type="application/json"
                    )
            
            response = await call_next(request)
            return response
            
        except jwt.ExpiredSignatureError:
            logger.warning("Expired JWT token")
            return Response(
                content='{"error": "Token expired"}',
                status_code=401,
                media_type="application/json"
            )
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid JWT token: %s", str(e))
            return Response(
                content='{"error": "Invalid token"}',
                status_code=401,
                media_type="application/json"
            )
        except Exception as e:
            logger.error("Authentication error: %s", str(e))
            return Response(
                content='{"error": "Authentication failed"}',
                status_code=500,
                media_type="application/json"
            )
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request headers."""
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
        
        try:
            scheme, token = authorization.split(" ", 1)
            if scheme.lower() != "bearer":
                return None
            return token
        except ValueError:
            return None
    
    def _validate_token(self, token: str) -> dict:
        """Validate JWT token and return user data."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.InvalidTokenError:
            raise
    
    def _is_protected_endpoint(self, path: str) -> bool:
        """Check if endpoint requires authentication."""
        # For now, all non-exempt endpoints are protected
        # In the future, this could be more sophisticated
        return path not in self.EXEMPT_PATHS 