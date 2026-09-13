import time
from typing import Optional, List
from quant_synthica_api.core.config import get_settings
from quant_synthica_api.core.exceptions import ProviderError
from quant_synthica_api.schemas.market import (
    QuoteResponse, QuoteData, HistoryResponse, OHLCVItem,
    DividendsResponse, DividendItem, SplitsResponse, SplitItem,
    AnalystRecommendationsResponse, UpgradesDowngradesResponse,
    OptionsChainResponse, NewsResponse
)
from quant_synthica_api.schemas.common import ResponseMetadata
from quant_synthica_api.services.symbol_resolver import SymbolResolver
from quant_synthica_api.services.cache_service import cache
from quant_synthica_api.providers.yfinance_provider import YFinanceProvider
from quant_synthica_api.services.fallback_service import FallbackService

settings = get_settings()

class MarketService:
    def __init__(
        self,
        yf_provider: YFinanceProvider,
        fallback_service: FallbackService
    ):
        self.yf = yf_provider
        self.fallback = fallback_service

    def get_quote(self, symbol_input: str) -> QuoteResponse:
        t0 = time.monotonic()
        resolved = SymbolResolver.resolve(symbol_input)
        cache_key = f"market:{resolved.canonical}:quote"

        cached_data = cache.get_json(cache_key)
        if cached_data:
            quote = QuoteData(**cached_data)
            return QuoteResponse(
                data=quote,
                metadata=ResponseMetadata(
                    source="cache",
                    cached=True,
                    latency_ms=(time.monotonic() - t0) * 1000
                )
            )

        quote_data, meta = self.fallback.get_quote_with_fallback(resolved)
        if not quote_data:
            raise ProviderError("market", f"Unable to fetch quote for symbol {symbol_input}")

        cache.set_json(cache_key, quote_data.model_dump(), ttl=settings.CACHE_QUOTE_TTL)

        return QuoteResponse(
            data=quote_data,
            metadata=ResponseMetadata(
                source=meta.successful_providers[0] if meta.successful_providers else "yfinance",
                cached=False,
                latency_ms=(time.monotonic() - t0) * 1000
            )
        )

    def get_history(
        self, symbol_input: str, period: str = "1y", interval: str = "1d"
    ) -> HistoryResponse:
        t0 = time.monotonic()
        resolved = SymbolResolver.resolve(symbol_input)
        cache_key = f"market:{resolved.canonical}:history:{period}:{interval}"

        cached_data = cache.get_json(cache_key)
        if cached_data:
            items = [OHLCVItem(**it) for it in cached_data]
            return HistoryResponse(
                symbol=resolved.canonical,
                period=period,
                interval=interval,
                count=len(items),
                data=items,
                metadata=ResponseMetadata(
                    source="cache",
                    cached=True,
                    latency_ms=(time.monotonic() - t0) * 1000
                )
            )

        res = self.yf.get_history(resolved.canonical, period=period, interval=interval)
        if not res.success or res.data is None:
            raise ProviderError("yfinance", res.error or f"Failed to fetch history for {resolved.canonical}")

        cache.set_json(cache_key, [item.model_dump() for item in res.data], ttl=settings.CACHE_DEFAULT_TTL)

        return HistoryResponse(
            symbol=resolved.canonical,
            period=period,
            interval=interval,
            count=len(res.data),
            data=res.data,
            metadata=ResponseMetadata(
                source=self.yf.name,
                cached=False,
                latency_ms=(time.monotonic() - t0) * 1000
            )
        )

    def get_dividends(self, symbol_input: str) -> DividendsResponse:
        t0 = time.monotonic()
        resolved = SymbolResolver.resolve(symbol_input)
        res = self.yf.get_dividends(resolved.canonical)
        if not res.success or res.data is None:
            raise ProviderError("yfinance", res.error or "Failed to fetch dividends")

        return DividendsResponse(
            symbol=resolved.canonical,
            count=len(res.data),
            data=res.data,
            metadata=ResponseMetadata(
                source=self.yf.name,
                cached=False,
                latency_ms=(time.monotonic() - t0) * 1000
            )
        )

    def get_splits(self, symbol_input: str) -> SplitsResponse:
        t0 = time.monotonic()
        resolved = SymbolResolver.resolve(symbol_input)
        res = self.yf.get_splits(resolved.canonical)
        if not res.success or res.data is None:
            raise ProviderError("yfinance", res.error or "Failed to fetch splits")

        return SplitsResponse(
            symbol=resolved.canonical,
            count=len(res.data),
            data=res.data,
            metadata=ResponseMetadata(
                source=self.yf.name,
                cached=False,
                latency_ms=(time.monotonic() - t0) * 1000
            )
        )

    # Extended market intelligence methods

    def get_recommendations(self, symbol_input: str) -> AnalystRecommendationsResponse:
        resolved = SymbolResolver.resolve(symbol_input)
        res = self.yf.get_recommendations(resolved.canonical)
        if not res.success or res.data is None:
            raise ProviderError("yfinance", res.error or "Failed to fetch analyst recommendations")
        return res.data

    def get_upgrades_downgrades(self, symbol_input: str, limit: int = 25) -> UpgradesDowngradesResponse:
        resolved = SymbolResolver.resolve(symbol_input)
        res = self.yf.get_upgrades_downgrades(resolved.canonical, limit=limit)
        if not res.success or res.data is None:
            raise ProviderError("yfinance", res.error or "Failed to fetch upgrades/downgrades")
        return res.data

    def get_options_chain(self, symbol_input: str, date: Optional[str] = None) -> OptionsChainResponse:
        resolved = SymbolResolver.resolve(symbol_input)
        res = self.yf.get_option_chain(resolved.canonical, date=date)
        if not res.success or res.data is None:
            raise ProviderError("yfinance", res.error or f"Failed to fetch option chain for {symbol_input}")
        return res.data

    def get_news(self, symbol_input: str) -> NewsResponse:
        resolved = SymbolResolver.resolve(symbol_input)
        res = self.yf.get_news(resolved.canonical)
        if not res.success or res.data is None:
            raise ProviderError("yfinance", res.error or "Failed to fetch news")
        return res.data
