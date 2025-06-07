"""Cache management utilities for high-performance data access."""

import json
import pickle
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import asyncio
import redis.asyncio as redis
from redis.exceptions import RedisError

from ..config.settings import settings
from ..config.logging import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Production-grade cache manager with Redis backend."""
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize cache manager.
        
        Args:
            redis_url: Redis connection URL (uses settings if None)
        """
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self) -> bool:
        """
        Connect to Redis server.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if not self._connected:
                self.redis = redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                
                # Test connection
                await self.redis.ping()
                self._connected = True
                logger.info("Cache manager connected to Redis")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Redis server."""
        try:
            if self.redis and self._connected:
                await self.redis.close()
                self._connected = False
                logger.info("Cache manager disconnected from Redis")
                
        except Exception as e:
            logger.error(f"Error disconnecting from Redis: {e}")
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        try:
            if not await self._ensure_connected():
                return default
                
            value = await self.redis.get(key)
            if value is None:
                return default
                
            # Try to deserialize JSON first, fallback to string
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return default
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            nx: Only set if key doesn't exist
            xx: Only set if key exists
            
        Returns:
            bool: True if set successfully, False otherwise
        """
        try:
            if not await self._ensure_connected():
                return False
                
            # Serialize value
            if isinstance(value, (dict, list, tuple)):
                serialized_value = json.dumps(value, default=str)
            else:
                serialized_value = str(value)
            
            result = await self.redis.set(
                key,
                serialized_value,
                ex=ttl,
                nx=nx,
                xx=xx
            )
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            if not await self._ensure_connected():
                return False
                
            result = await self.redis.delete(key)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key to check
            
        Returns:
            bool: True if key exists, False otherwise
        """
        try:
            if not await self._ensure_connected():
                return False
                
            result = await self.redis.exists(key)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False
    
    async def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment counter in cache.
        
        Args:
            key: Cache key
            amount: Amount to increment by
            
        Returns:
            New value or None if error
        """
        try:
            if not await self._ensure_connected():
                return None
                
            return await self.redis.incrby(key, amount)
            
        except Exception as e:
            logger.error(f"Error incrementing cache key {key}: {e}")
            return None
    
    async def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration time for key.
        
        Args:
            key: Cache key
            ttl: Time to live in seconds
            
        Returns:
            bool: True if expiration set, False otherwise
        """
        try:
            if not await self._ensure_connected():
                return False
                
            return await self.redis.expire(key, ttl)
            
        except Exception as e:
            logger.error(f"Error setting expiration for cache key {key}: {e}")
            return False
    
    async def hget(self, hash_key: str, field: str, default: Any = None) -> Any:
        """
        Get field from hash.
        
        Args:
            hash_key: Hash key
            field: Field name
            default: Default value if field not found
            
        Returns:
            Field value or default
        """
        try:
            if not await self._ensure_connected():
                return default
                
            value = await self.redis.hget(hash_key, field)
            if value is None:
                return default
                
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"Error getting hash field {hash_key}.{field}: {e}")
            return default
    
    async def hset(self, hash_key: str, field: str, value: Any) -> bool:
        """
        Set field in hash.
        
        Args:
            hash_key: Hash key
            field: Field name
            value: Field value
            
        Returns:
            bool: True if set successfully, False otherwise
        """
        try:
            if not await self._ensure_connected():
                return False
                
            # Serialize value
            if isinstance(value, (dict, list, tuple)):
                serialized_value = json.dumps(value, default=str)
            else:
                serialized_value = str(value)
            
            result = await self.redis.hset(hash_key, field, serialized_value)
            return True
            
        except Exception as e:
            logger.error(f"Error setting hash field {hash_key}.{field}: {e}")
            return False
    
    async def hgetall(self, hash_key: str) -> Dict[str, Any]:
        """
        Get all fields from hash.
        
        Args:
            hash_key: Hash key
            
        Returns:
            Dict with all hash fields
        """
        try:
            if not await self._ensure_connected():
                return {}
                
            result = await self.redis.hgetall(hash_key)
            
            # Deserialize values
            deserialized = {}
            for field, value in result.items():
                try:
                    deserialized[field] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    deserialized[field] = value
            
            return deserialized
            
        except Exception as e:
            logger.error(f"Error getting hash {hash_key}: {e}")
            return {}
    
    async def cache_health_status(
        self,
        service_name: str,
        health_data: Dict[str, Any],
        ttl: int = 30
    ) -> bool:
        """
        Cache health status data.
        
        Args:
            service_name: Service name
            health_data: Health status data
            ttl: Time to live in seconds
            
        Returns:
            bool: True if cached successfully
        """
        key = f"health_status:{service_name}"
        return await self.set(key, health_data, ttl=ttl)
    
    async def get_cached_health_status(
        self,
        service_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached health status.
        
        Args:
            service_name: Service name
            
        Returns:
            Cached health data or None
        """
        key = f"health_status:{service_name}"
        return await self.get(key)
    
    async def cache_metrics(
        self,
        metric_key: str,
        metrics_data: Dict[str, Any],
        ttl: int = 300
    ) -> bool:
        """
        Cache metrics data.
        
        Args:
            metric_key: Metrics cache key
            metrics_data: Metrics data
            ttl: Time to live in seconds (default: 5 minutes)
            
        Returns:
            bool: True if cached successfully
        """
        key = f"metrics:{metric_key}"
        return await self.set(key, metrics_data, ttl=ttl)
    
    async def get_cached_metrics(
        self,
        metric_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached metrics data.
        
        Args:
            metric_key: Metrics cache key
            
        Returns:
            Cached metrics data or None
        """
        key = f"metrics:{metric_key}"
        return await self.get(key)
    
    async def _ensure_connected(self) -> bool:
        """Ensure Redis connection is active."""
        if not self._connected:
            return await self.connect()
        
        try:
            # Test connection
            await self.redis.ping()
            return True
        except Exception:
            # Reconnect if ping fails
            self._connected = False
            return await self.connect()
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache statistics
        """
        try:
            if not await self._ensure_connected():
                return {
                    'connected': False,
                    'error': 'Not connected to Redis'
                }
            
            info = await self.redis.info()
            
            return {
                'connected': True,
                'redis_version': info.get('redis_version'),
                'used_memory': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'total_commands_processed': info.get('total_commands_processed'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(
                    info.get('keyspace_hits', 0),
                    info.get('keyspace_misses', 0)
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {
                'connected': False,
                'error': str(e)
            }
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage."""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2) 