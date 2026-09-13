import json
import time
from typing import Optional, Any, Dict
import redis
from quant_synthica_api.core.config import get_settings
from quant_synthica_api.core.logging import logger

settings = get_settings()

class InMemoryCache:
    """In-memory cache with TTL expiration as fallback when Redis is unavailable."""
    def __init__(self):
        self._store: Dict[str, tuple[float, str]] = {}

    def get(self, key: str) -> Optional[str]:
        if key in self._store:
            expiry, val = self._store[key]
            if time.time() < expiry:
                return val
            else:
                del self._store[key]
        return None

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        expiry = time.time() + (ex if ex else 3600)
        self._store[key] = (expiry, value)
        return True

    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    def clear(self):
        self._store.clear()

class CacheService:
    def __init__(self):
        self.enabled = settings.CACHE_ENABLED
        self.redis_client: Optional[redis.Redis] = None
        self.memory_fallback = InMemoryCache()
        self.is_redis_connected = False
        self._init_redis()

    def _init_redis(self):
        if not self.enabled:
            return
        try:
            client = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=1.0,
                socket_connect_timeout=1.0
            )
            client.ping()
            self.redis_client = client
            self.is_redis_connected = True
            logger.info("Connected to Redis cache successfully.")
        except Exception as e:
            logger.warning(f"Redis not available ({e}). Using in-memory cache fallback.")
            self.redis_client = None
            self.is_redis_connected = False

    def get_json(self, key: str) -> Optional[Any]:
        if not self.enabled:
            return None
        try:
            if self.is_redis_connected and self.redis_client:
                data = self.redis_client.get(key)
            else:
                data = self.memory_fallback.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.debug(f"Cache get error for {key}: {e}")
        return None

    def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if not self.enabled:
            return False
        effective_ttl = ttl or settings.CACHE_DEFAULT_TTL
        try:
            payload = json.dumps(value, default=str)
            if self.is_redis_connected and self.redis_client:
                self.redis_client.set(key, payload, ex=effective_ttl)
            else:
                self.memory_fallback.set(key, payload, ex=effective_ttl)
            return True
        except Exception as e:
            logger.debug(f"Cache set error for {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        try:
            if self.is_redis_connected and self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                return self.memory_fallback.delete(key)
        except Exception as e:
            logger.debug(f"Cache delete error for {key}: {e}")
            return False

# Global cache singleton
cache = CacheService()
