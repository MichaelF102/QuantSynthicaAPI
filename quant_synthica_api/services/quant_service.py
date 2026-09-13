import time
from typing import Optional
from quant_synthica_api.core.config import get_settings
from quant_synthica_api.core.exceptions import ProviderError
from quant_synthica_api.schemas.quant import (
    ReturnsResponse, ReturnsMetrics, RiskResponse, RiskMetrics,
    VolatilityResponse, VolatilityMetrics, TechnicalResponse,
    TechnicalIndicators, QuantSummaryResponse, QuantSummaryData
)
from quant_synthica_api.schemas.common import ResponseMetadata
from quant_synthica_api.services.symbol_resolver import SymbolResolver
from quant_synthica_api.services.cache_service import cache
from quant_synthica_api.providers.yfinance_provider import YFinanceProvider
from quant_synthica_api.quant.engine import QuantEngine

settings = get_settings()

class QuantService:
    def __init__(self, yf_provider: YFinanceProvider):
        self.yf = yf_provider

    def _get_history_for_quant(self, canonical: str, period: str = "1y"):
        cache_key = f"market:{canonical}:history:{period}:1d"
        cached = cache.get_json(cache_key)
        if cached:
            from quant_synthica_api.schemas.market import OHLCVItem
            return [OHLCVItem(**it) for it in cached]

        res = self.yf.get_history(canonical, period=period, interval="1d")
        if not res.success or not res.data:
            raise ProviderError("yfinance", res.error or f"Failed to fetch history for {canonical}")
        
        cache.set_json(cache_key, [item.model_dump() for item in res.data], ttl=settings.CACHE_DEFAULT_TTL)
        return res.data

    def get_returns(self, symbol_input: str, period: str = "1y") -> ReturnsResponse:
        t0 = time.monotonic()
        resolved = SymbolResolver.resolve(symbol_input)
        cache_key = f"quant:{resolved.canonical}:returns:{period}"

        cached = cache.get_json(cache_key)
        if cached:
            return ReturnsResponse(
                data=ReturnsMetrics(**cached),
                metadata=ResponseMetadata(source="cache", cached=True, latency_ms=(time.monotonic() - t0) * 1000)
            )

        items = self._get_history_for_quant(resolved.canonical, period=period)
        ret = QuantEngine.compute_returns(items, resolved.canonical)
        cache.set_json(cache_key, ret.model_dump(), ttl=settings.CACHE_QUANT_TTL)

        return ReturnsResponse(
            data=ret,
            metadata=ResponseMetadata(source="quant_engine", cached=False, latency_ms=(time.monotonic() - t0) * 1000)
        )

    def get_risk(self, symbol_input: str, period: str = "1y", risk_free_rate: float = 0.06) -> RiskResponse:
        t0 = time.monotonic()
        resolved = SymbolResolver.resolve(symbol_input)
        cache_key = f"quant:{resolved.canonical}:risk:{period}:{risk_free_rate}"

        cached = cache.get_json(cache_key)
        if cached:
            return RiskResponse(
                data=RiskMetrics(**cached),
                metadata=ResponseMetadata(source="cache", cached=True, latency_ms=(time.monotonic() - t0) * 1000)
            )

        items = self._get_history_for_quant(resolved.canonical, period=period)
        
        # Benchmark for beta: ^NSEI for India, SPY for US
        benchmark_sym = "^NSEI" if resolved.country == "IN" else "SPY"
        benchmark_items = None
        try:
            benchmark_items = self._get_history_for_quant(benchmark_sym, period=period)
        except Exception:
            pass

        risk = QuantEngine.compute_risk(items, resolved.canonical, risk_free_rate=risk_free_rate)
        # Re-calc beta if benchmark available
        if benchmark_items:
            from quant_synthica_api.quant.risk import calculate_risk
            risk = calculate_risk(items, resolved.canonical, risk_free_rate=risk_free_rate, benchmark_items=benchmark_items)

        cache.set_json(cache_key, risk.model_dump(), ttl=settings.CACHE_QUANT_TTL)

        return RiskResponse(
            data=risk,
            metadata=ResponseMetadata(source="quant_engine", cached=False, latency_ms=(time.monotonic() - t0) * 1000)
        )

    def get_volatility(self, symbol_input: str, period: str = "1y") -> VolatilityResponse:
        t0 = time.monotonic()
        resolved = SymbolResolver.resolve(symbol_input)
        cache_key = f"quant:{resolved.canonical}:volatility:{period}"

        cached = cache.get_json(cache_key)
        if cached:
            return VolatilityResponse(
                data=VolatilityMetrics(**cached),
                metadata=ResponseMetadata(source="cache", cached=True, latency_ms=(time.monotonic() - t0) * 1000)
            )

        items = self._get_history_for_quant(resolved.canonical, period=period)
        vol = QuantEngine.compute_volatility(items, resolved.canonical)
        cache.set_json(cache_key, vol.model_dump(), ttl=settings.CACHE_QUANT_TTL)

        return VolatilityResponse(
            data=vol,
            metadata=ResponseMetadata(source="quant_engine", cached=False, latency_ms=(time.monotonic() - t0) * 1000)
        )

    def get_technical(self, symbol_input: str, period: str = "1y") -> TechnicalResponse:
        t0 = time.monotonic()
        resolved = SymbolResolver.resolve(symbol_input)
        cache_key = f"quant:{resolved.canonical}:technical:{period}"

        cached = cache.get_json(cache_key)
        if cached:
            return TechnicalResponse(
                data=TechnicalIndicators(**cached),
                metadata=ResponseMetadata(source="cache", cached=True, latency_ms=(time.monotonic() - t0) * 1000)
            )

        items = self._get_history_for_quant(resolved.canonical, period=period)
        tech = QuantEngine.compute_technical(items, resolved.canonical)
        cache.set_json(cache_key, tech.model_dump(), ttl=settings.CACHE_QUANT_TTL)

        return TechnicalResponse(
            data=tech,
            metadata=ResponseMetadata(source="quant_engine", cached=False, latency_ms=(time.monotonic() - t0) * 1000)
        )

    def get_summary(self, symbol_input: str, period: str = "1y", risk_free_rate: float = 0.06) -> QuantSummaryResponse:
        t0 = time.monotonic()
        resolved = SymbolResolver.resolve(symbol_input)
        cache_key = f"quant:{resolved.canonical}:summary:{period}"

        cached = cache.get_json(cache_key)
        if cached:
            return QuantSummaryResponse(
                data=QuantSummaryData(**cached),
                metadata=ResponseMetadata(source="cache", cached=True, latency_ms=(time.monotonic() - t0) * 1000)
            )

        items = self._get_history_for_quant(resolved.canonical, period=period)
        summary = QuantEngine.compute_summary(items, resolved.canonical, risk_free_rate=risk_free_rate)
        cache.set_json(cache_key, summary.model_dump(), ttl=settings.CACHE_QUANT_TTL)

        return QuantSummaryResponse(
            data=summary,
            metadata=ResponseMetadata(source="quant_engine", cached=False, latency_ms=(time.monotonic() - t0) * 1000)
        )
