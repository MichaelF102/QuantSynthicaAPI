from typing import Optional
from quant_synthica_api.schemas.stock_profile import StockProfileResponse
from quant_synthica_api.services.symbol_resolver import SymbolResolver
from quant_synthica_api.services.normalization_service import NormalizationService
from quant_synthica_api.services.market_service import MarketService
from quant_synthica_api.services.fundamentals_service import FundamentalsService
from quant_synthica_api.services.quant_service import QuantService
from quant_synthica_api.services.cache_service import cache
from quant_synthica_api.core.config import get_settings
from quant_synthica_api.core.logging import logger

settings = get_settings()

class StockProfileService:
    def __init__(
        self,
        market_service: MarketService,
        fundamentals_service: FundamentalsService,
        quant_service: QuantService
    ):
        self.market = market_service
        self.fundamentals = fundamentals_service
        self.quant = quant_service

    def get_stock_profile(self, symbol_input: str) -> StockProfileResponse:
        resolved = SymbolResolver.resolve(symbol_input)
        cache_key = f"stock_profile:{resolved.canonical}"

        cached = cache.get_json(cache_key)
        if cached:
            return StockProfileResponse(**cached)

        # 1. Fetch Quote
        quote_data = None
        quote_source = "yfinance"
        try:
            q_res = self.market.get_quote(resolved.canonical)
            quote_data = q_res.data
            quote_source = q_res.metadata.source
        except Exception as e:
            logger.warning(f"Failed to get quote for {symbol_input} in profile: {e}")

        # 2. Fetch Fundamentals
        fund_data = None
        fund_source = "screener"
        try:
            f_res = self.fundamentals.get_unified_fundamentals(resolved.symbol)
            fund_data = f_res.data
            fund_source = "screener"
        except Exception as e:
            logger.warning(f"Failed to get fundamentals for {symbol_input} in profile: {e}")

        # 3. Fetch Quant Summary
        quant_data = None
        quant_source = "quant_engine"
        try:
            qk_res = self.quant.get_summary(resolved.canonical, period="1y")
            quant_data = qk_res.data
            quant_source = qk_res.metadata.source
        except Exception as e:
            logger.warning(f"Failed to get quant summary for {symbol_input} in profile: {e}")

        # 4. Normalize & Unify
        profile = NormalizationService.build_unified_profile(
            resolved=resolved,
            quote=quote_data,
            quote_source=quote_source,
            fundamentals=fund_data,
            fundamentals_source=fund_source,
            quant_summary=quant_data,
            quant_source=quant_source
        )

        cache.set_json(cache_key, profile.model_dump(), ttl=settings.CACHE_DEFAULT_TTL)
        return profile
