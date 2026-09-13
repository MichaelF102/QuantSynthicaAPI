import time
from typing import Optional
from quant_synthica_api.core.config import get_settings
from quant_synthica_api.core.exceptions import ProviderError
from quant_synthica_api.schemas.screener import (
    ScreenerQueryRequest, ScreenerFilter, ScreenerResponse,
    GenericScreenerRequest, MultiAssetScreenerResponse
)
from quant_synthica_api.providers.tradingview_provider import TradingViewProvider
from quant_synthica_api.services.cache_service import cache

settings = get_settings()

class ScreenerService:
    def __init__(self, tv_provider: TradingViewProvider):
        self.tv = tv_provider

    def query(self, req: ScreenerQueryRequest) -> ScreenerResponse:
        t0 = time.monotonic()
        cache_key = f"screener:query:{hash(req.model_dump_json())}"

        cached = cache.get_json(cache_key)
        if cached:
            resp = ScreenerResponse(**cached)
            resp.metadata.cached = True
            return resp

        res = self.tv.query_screener(req)
        if not res.success or res.data is None:
            raise ProviderError("tradingview", res.error or "Screener query failed")

        cache.set_json(cache_key, res.data.model_dump(), ttl=settings.CACHE_SCREENER_TTL)
        return res.data

    def query_multi_asset(self, asset_class: str, req: GenericScreenerRequest) -> MultiAssetScreenerResponse:
        cache_key = f"screener:{asset_class}:{hash(req.model_dump_json())}"
        cached = cache.get_json(cache_key)
        if cached:
            resp = MultiAssetScreenerResponse(**cached)
            resp.metadata.cached = True
            return resp

        res = self.tv.query_multi_asset(asset_class, req)
        if not res.success or res.data is None:
            raise ProviderError("tradingview", res.error or f"Multi-asset screener failed for {asset_class}")

        cache.set_json(cache_key, res.data.model_dump(), ttl=settings.CACHE_SCREENER_TTL)
        return res.data

    def get_value_stocks(self, market: str = "india", limit: int = 20) -> ScreenerResponse:
        req = ScreenerQueryRequest(
            market=market,
            exchange="NSE" if market.lower() == "india" else None,
            filters=ScreenerFilter(pe_max=25.0, pb_max=3.5, dividend_yield_min=0.5),
            sort_by="market_cap_basic",
            sort_order="desc",
            limit=limit
        )
        return self.query(req)

    def get_growth_stocks(self, market: str = "india", limit: int = 20) -> ScreenerResponse:
        req = ScreenerQueryRequest(
            market=market,
            exchange="NSE" if market.lower() == "india" else None,
            filters=ScreenerFilter(roe_min=15.0, market_cap_min=50000000000),
            sort_by="return_on_equity",
            sort_order="desc",
            limit=limit
        )
        return self.query(req)

    def get_momentum_stocks(self, market: str = "india", limit: int = 20) -> ScreenerResponse:
        req = ScreenerQueryRequest(
            market=market,
            exchange="NSE" if market.lower() == "india" else None,
            filters=ScreenerFilter(rsi_min=50.0, rsi_max=75.0, volume_min=100000),
            sort_by="volume",
            sort_order="desc",
            limit=limit
        )
        return self.query(req)

    def get_dividend_stocks(self, market: str = "india", limit: int = 20) -> ScreenerResponse:
        req = ScreenerQueryRequest(
            market=market,
            exchange="NSE" if market.lower() == "india" else None,
            filters=ScreenerFilter(dividend_yield_min=2.5),
            sort_by="dividend_yield_recent",
            sort_order="desc",
            limit=limit
        )
        return self.query(req)
