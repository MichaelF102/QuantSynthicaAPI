import pytest
from quant_synthica_api.services.cache_service import CacheService

def test_cache_set_get_delete():
    cache = CacheService()
    # Force memory fallback for deterministic unit testing
    cache.is_redis_connected = False

    key = "test:stock:reliance"
    val = {"price": 1250.0, "symbol": "RELIANCE.NS"}
    
    assert cache.set_json(key, val, ttl=60) is True
    retrieved = cache.get_json(key)
    assert retrieved == val

    assert cache.delete(key) is True
    assert cache.get_json(key) is None
