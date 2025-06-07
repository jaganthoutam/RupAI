"""
Redis Connection Manager
Enterprise-grade Redis connection handling with clustering support.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import timedelta

import redis.asyncio as redis
from redis.asyncio import Redis, ConnectionPool
from redis.exceptions import ConnectionError, TimeoutError, RedisError

from app.config.settings import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Enterprise Redis client with high availability features.
    
    Features:
    - Connection pooling
    - Automatic retry logic
    - Health monitoring
    - Serialization support
    - Pipeline operations
    - Pub/Sub support
    """
    
    def __init__(self):
        self.client: Optional[Redis] = None
        self.pool: Optional[ConnectionPool] = None
        self._connected = False
        self._connection_stats = {
            "connections_created": 0,
            "commands_executed": 0,
            "errors": 0
        }
        
    async def connect(self) -> None:
        """Initialize Redis connection with enterprise features."""
        try:
            logger.info("🔄 Connecting to Redis...")
            
            # Create connection pool
            self.pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_POOL_SIZE,
                retry_on_timeout=True,
                retry_on_error=[ConnectionError, TimeoutError],
                health_check_interval=30,
                socket_keepalive=True,
                socket_keepalive_options={},
                socket_connect_timeout=5,
                socket_timeout=5,
                encoding='utf-8',
                decode_responses=True
            )
            
            # Create Redis client
            self.client = Redis(
                connection_pool=self.pool,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            await self.client.ping()
            info = await self.client.info()
            
            logger.info(
                "✅ Redis connected - Version: %s, Mode: %s",
                info.get('redis_version', 'unknown'),
                info.get('redis_mode', 'standalone')
            )
            
            self._connected = True
            self._connection_stats["connections_created"] += 1
            
        except Exception as e:
            logger.error("❌ Failed to connect to Redis: %s", str(e))
            raise
    
    async def disconnect(self) -> None:
        """Gracefully close Redis connections."""
        if self.client:
            logger.info("🔄 Closing Redis connections...")
            await self.client.close()
            self._connected = False
            logger.info("✅ Redis connections closed")
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive Redis health check."""
        if not self._connected or not self.client:
            return {
                "status": "unhealthy",
                "error": "Redis not connected"
            }
        
        try:
            # Test basic operations
            start_time = asyncio.get_event_loop().time()
            await self.client.ping()
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Get Redis info
            info = await self.client.info()
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "redis_version": info.get('redis_version'),
                "uptime_seconds": info.get('uptime_in_seconds'),
                "connected_clients": info.get('connected_clients'),
                "used_memory": info.get('used_memory_human'),
                "total_commands_processed": info.get('total_commands_processed'),
                "connection_stats": self._connection_stats.copy()
            }
            
        except Exception as e:
            logger.error("Redis health check failed: %s", str(e))
            self._connection_stats["errors"] += 1
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    # Key-Value Operations
    async def set(
        self, 
        key: str, 
        value: Any, 
        ex: Optional[Union[int, timedelta]] = None,
        px: Optional[Union[int, timedelta]] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """Set key-value pair with options."""
        try:
            serialized_value = json.dumps(value) if not isinstance(value, str) else value
            result = await self.client.set(key, serialized_value, ex=ex, px=px, nx=nx, xx=xx)
            self._connection_stats["commands_executed"] += 1
            return result
        except Exception as e:
            logger.error("Redis SET error for key %s: %s", key, str(e))
            self._connection_stats["errors"] += 1
            raise
    
    async def get(self, key: str, deserialize: bool = True) -> Optional[Any]:
        """Get value by key with optional deserialization."""
        try:
            value = await self.client.get(key)
            self._connection_stats["commands_executed"] += 1
            
            if value is None:
                return None
            
            if deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            return value
            
        except Exception as e:
            logger.error("Redis GET error for key %s: %s", key, str(e))
            self._connection_stats["errors"] += 1
            raise
    
    async def delete(self, *keys: str) -> int:
        """Delete one or more keys."""
        try:
            result = await self.client.delete(*keys)
            self._connection_stats["commands_executed"] += 1
            return result
        except Exception as e:
            logger.error("Redis DELETE error for keys %s: %s", keys, str(e))
            self._connection_stats["errors"] += 1
            raise
    
    async def exists(self, *keys: str) -> int:
        """Check if keys exist."""
        try:
            result = await self.client.exists(*keys)
            self._connection_stats["commands_executed"] += 1
            return result
        except Exception as e:
            logger.error("Redis EXISTS error for keys %s: %s", keys, str(e))
            self._connection_stats["errors"] += 1
            raise
    
    async def expire(self, key: str, time: Union[int, timedelta]) -> bool:
        """Set expiration for key."""
        try:
            result = await self.client.expire(key, time)
            self._connection_stats["commands_executed"] += 1
            return result
        except Exception as e:
            logger.error("Redis EXPIRE error for key %s: %s", key, str(e))
            self._connection_stats["errors"] += 1
            raise
    
    async def ttl(self, key: str) -> int:
        """Get time to live for key."""
        try:
            result = await self.client.ttl(key)
            self._connection_stats["commands_executed"] += 1
            return result
        except Exception as e:
            logger.error("Redis TTL error for key %s: %s", key, str(e))
            self._connection_stats["errors"] += 1
            raise
    
    # Hash Operations
    async def hset(self, name: str, mapping: Dict[str, Any]) -> int:
        """Set hash fields."""
        try:
            # Serialize complex values
            serialized_mapping = {}
            for field, value in mapping.items():
                if isinstance(value, (dict, list, tuple)):
                    serialized_mapping[field] = json.dumps(value)
                else:
                    serialized_mapping[field] = str(value)
            
            result = await self.client.hset(name, mapping=serialized_mapping)
            self._connection_stats["commands_executed"] += 1
            return result
        except Exception as e:
            logger.error("Redis HSET error for hash %s: %s", name, str(e))
            self._connection_stats["errors"] += 1
            raise
    
    async def hget(self, name: str, key: str, deserialize: bool = True) -> Optional[Any]:
        """Get hash field value."""
        try:
            value = await self.client.hget(name, key)
            self._connection_stats["commands_executed"] += 1
            
            if value is None:
                return None
            
            if deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            return value
            
        except Exception as e:
            logger.error("Redis HGET error for hash %s field %s: %s", name, key, str(e))
            self._connection_stats["errors"] += 1
            raise
    
    async def hgetall(self, name: str, deserialize: bool = True) -> Dict[str, Any]:
        """Get all hash fields and values."""
        try:
            result = await self.client.hgetall(name)
            self._connection_stats["commands_executed"] += 1
            
            if not deserialize:
                return result
            
            # Deserialize values
            deserialized = {}
            for field, value in result.items():
                try:
                    deserialized[field] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    deserialized[field] = value
            
            return deserialized
            
        except Exception as e:
            logger.error("Redis HGETALL error for hash %s: %s", name, str(e))
            self._connection_stats["errors"] += 1
            raise
    
    # List Operations
    async def lpush(self, name: str, *values: Any) -> int:
        """Push values to the left of list."""
        try:
            serialized_values = [
                json.dumps(v) if not isinstance(v, str) else v 
                for v in values
            ]
            result = await self.client.lpush(name, *serialized_values)
            self._connection_stats["commands_executed"] += 1
            return result
        except Exception as e:
            logger.error("Redis LPUSH error for list %s: %s", name, str(e))
            self._connection_stats["errors"] += 1
            raise
    
    async def rpop(self, name: str, deserialize: bool = True) -> Optional[Any]:
        """Pop value from the right of list."""
        try:
            value = await self.client.rpop(name)
            self._connection_stats["commands_executed"] += 1
            
            if value is None:
                return None
            
            if deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            return value
            
        except Exception as e:
            logger.error("Redis RPOP error for list %s: %s", name, str(e))
            self._connection_stats["errors"] += 1
            raise
    
    # Cache Helper Methods
    async def cache_set(
        self, 
        key: str, 
        value: Any, 
        ttl: Union[int, timedelta] = timedelta(hours=1)
    ) -> bool:
        """Set cache value with TTL."""
        return await self.set(key, value, ex=ttl)
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """Get cache value."""
        return await self.get(key, deserialize=True)
    
    async def cache_delete(self, key: str) -> bool:
        """Delete cache value."""
        return bool(await self.delete(key))
    
    # Utility Methods
    async def flush_db(self) -> bool:
        """Flush current database (use with caution)."""
        if settings.ENVIRONMENT == "development":
            try:
                await self.client.flushdb()
                self._connection_stats["commands_executed"] += 1
                return True
            except Exception as e:
                logger.error("Redis FLUSHDB error: %s", str(e))
                self._connection_stats["errors"] += 1
                raise
        else:
            raise RuntimeError("FLUSHDB is only allowed in development environment")
    
    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._connected
    
    @property
    def connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return self._connection_stats.copy() 