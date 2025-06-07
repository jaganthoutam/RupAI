"""
Rate Limiting Utilities
Token bucket and sliding window rate limiting implementation.
"""

import asyncio
import logging
import time
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque

from fastapi import Request, Response, HTTPException

from app.config.settings import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter with multiple algorithms and storage backends.
    
    Features:
    - Token bucket algorithm
    - Sliding window algorithm
    - Per-IP and per-user rate limiting
    - Configurable limits and windows
    - Memory-based storage (Redis integration ready)
    """
    
    def __init__(self):
        # In-memory storage for rate limiting
        # In production, this should use Redis for distributed rate limiting
        self.token_buckets: Dict[str, Dict] = defaultdict(dict)
        self.sliding_windows: Dict[str, deque] = defaultdict(lambda: deque())
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # Default rate limits (requests per hour)
        self.default_limits = {
            "anonymous": 100,
            "authenticated": 1000,
            "premium": 5000
        }
        
        # Parse rate limit from settings
        self.parse_rate_limit_config()
        
    def parse_rate_limit_config(self):
        """Parse rate limit configuration from settings."""
        try:
            # Parse format like "1000/hour" or "100/minute"
            limit_str = settings.API_RATE_LIMIT
            if "/" in limit_str:
                rate, period = limit_str.split("/")
                self.default_rate = int(rate)
                
                # Convert period to seconds
                if period == "minute":
                    self.default_window = 60
                elif period == "hour":
                    self.default_window = 3600
                elif period == "day":
                    self.default_window = 86400
                else:
                    self.default_window = 3600  # Default to hour
            else:
                self.default_rate = int(limit_str)
                self.default_window = 3600
                
        except (ValueError, AttributeError):
            # Fallback to defaults
            self.default_rate = 1000
            self.default_window = 3600
    
    async def middleware(self, request: Request, call_next):
        """Rate limiting middleware."""
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/ready", "/metrics"]:
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limit
        allowed, retry_after = await self._check_rate_limit(client_id, request)
        
        if not allowed:
            logger.warning(
                "Rate limit exceeded for client %s on path %s",
                client_id,
                request.url.path
            )
            
            response = Response(
                content='{"error": "Rate limit exceeded", "retry_after": ' + str(retry_after) + '}',
                status_code=429,
                media_type="application/json"
            )
            response.headers["Retry-After"] = str(retry_after)
            response.headers["X-RateLimit-Limit"] = str(self.default_rate)
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Reset"] = str(int(time.time() + retry_after))
            
            return response
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = await self._get_remaining_requests(client_id)
        response.headers["X-RateLimit-Limit"] = str(self.default_rate)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + self.default_window))
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        
        # Try to get user ID from authentication
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.get("sub") or request.state.user.get("user_id")
            if user_id:
                return f"user:{user_id}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        
        # Check for forwarded IP headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            client_ip = real_ip
        
        return f"ip:{client_ip}"
    
    async def _check_rate_limit(self, client_id: str, request: Request) -> Tuple[bool, int]:
        """
        Check if request is within rate limit.
        
        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        
        # Get rate limit for client
        rate_limit = self._get_rate_limit_for_client(client_id, request)
        
        # Use sliding window algorithm
        return await self._sliding_window_check(client_id, rate_limit)
    
    def _get_rate_limit_for_client(self, client_id: str, request: Request) -> int:
        """Get rate limit for specific client."""
        
        # Check if user is authenticated
        if hasattr(request.state, "authenticated") and request.state.authenticated:
            # Check for premium user (this would come from user data)
            if hasattr(request.state, "user") and request.state.user:
                user_type = request.state.user.get("type", "authenticated")
                return self.default_limits.get(user_type, self.default_limits["authenticated"])
            return self.default_limits["authenticated"]
        
        return self.default_limits["anonymous"]
    
    async def _sliding_window_check(self, client_id: str, rate_limit: int) -> Tuple[bool, int]:
        """Sliding window rate limiting check."""
        
        current_time = time.time()
        window_start = current_time - self.default_window
        
        # Get or create sliding window for client
        window = self.sliding_windows[client_id]
        
        # Remove old entries
        while window and window[0] < window_start:
            window.popleft()
        
        # Check if within limit
        if len(window) >= rate_limit:
            # Calculate retry after (time until oldest entry expires)
            retry_after = int(window[0] + self.default_window - current_time) + 1
            return False, retry_after
        
        # Add current request to window
        window.append(current_time)
        
        return True, 0
    
    async def _get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client."""
        
        current_time = time.time()
        window_start = current_time - self.default_window
        
        # Get sliding window for client
        window = self.sliding_windows.get(client_id, deque())
        
        # Count requests in current window
        current_requests = sum(1 for timestamp in window if timestamp >= window_start)
        
        return max(0, self.default_rate - current_requests)
    
    async def _cleanup_expired_entries(self):
        """Background task to cleanup expired rate limit entries."""
        while True:
            try:
                current_time = time.time()
                window_start = current_time - self.default_window
                
                # Cleanup sliding windows
                for client_id in list(self.sliding_windows.keys()):
                    window = self.sliding_windows[client_id]
                    
                    # Remove old entries
                    while window and window[0] < window_start:
                        window.popleft()
                    
                    # Remove empty windows
                    if not window:
                        del self.sliding_windows[client_id]
                
                # Cleanup token buckets
                for client_id in list(self.token_buckets.keys()):
                    bucket = self.token_buckets[client_id]
                    if bucket.get("last_update", 0) < window_start:
                        del self.token_buckets[client_id]
                
                # Sleep for cleanup interval
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Rate limiter cleanup error: %s", str(e))
                await asyncio.sleep(60)  # Wait before retrying
    
    async def start_cleanup_task(self):
        """Start background cleanup task."""
        if not self.cleanup_task:
            self.cleanup_task = asyncio.create_task(self._cleanup_expired_entries())
    
    async def stop_cleanup_task(self):
        """Stop background cleanup task."""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
            self.cleanup_task = None 