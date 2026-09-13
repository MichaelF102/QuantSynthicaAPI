from fastapi import APIRouter
from quant_synthica_api.core.config import get_settings
from quant_synthica_api.services.cache_service import cache
from quant_synthica_api.services.container import container
from datetime import datetime, timezone

router = APIRouter(tags=["Health"])

@router.get("/health", summary="Health check and status of upstream providers")
def health_check():
    settings = get_settings()

    yf_ok = container.yf_provider.health_check()
    tv_ok = container.tv_provider.health_check()
    sc_ok = container.screener_provider.health_check()

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": settings.API_VERSION,
        "providers": {
            "yfinance": "healthy" if yf_ok else "unhealthy",
            "tradingview": "healthy" if tv_ok else "unhealthy",
            "screener_in": "healthy" if sc_ok else "unhealthy"
        },
        "cache": {
            "enabled": settings.CACHE_ENABLED,
            "type": "redis" if cache.is_redis_connected else "in_memory_fallback"
        }
    }
