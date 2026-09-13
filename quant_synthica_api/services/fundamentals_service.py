import time
from typing import Optional
from quant_synthica_api.core.config import get_settings
from quant_synthica_api.core.exceptions import ProviderError
from quant_synthica_api.schemas.fundamentals import (
    UnifiedFundamentalsResponse, UnifiedFundamentalsData, FinancialStatementResponse,
    FinancialStatementData, RatiosResponse, RatiosData, ShareholdingResponse,
    HoldersResponse, InsiderTransactionsResponse, SustainabilityResponse,
    PeersResponse, CorporateAnalysisResponse, DocumentsResponse
)
from quant_synthica_api.schemas.common import ResponseMetadata, MultiSourceMetadata
from quant_synthica_api.services.symbol_resolver import SymbolResolver
from quant_synthica_api.services.cache_service import cache
from quant_synthica_api.providers.screener_provider import ScreenerProvider
from quant_synthica_api.providers.yfinance_provider import YFinanceProvider
from quant_synthica_api.services.fallback_service import FallbackService

settings = get_settings()

class FundamentalsService:
    def __init__(
        self,
        screener_provider: ScreenerProvider,
        yf_provider: YFinanceProvider,
        fallback_service: FallbackService
    ):
        self.screener = screener_provider
        self.yf = yf_provider
        self.fallback = fallback_service

    def get_unified_fundamentals(self, symbol_input: str) -> UnifiedFundamentalsResponse:
        t0 = time.monotonic()
        resolved = SymbolResolver.resolve(symbol_input)
        cache_key = f"fundamentals:{resolved.canonical}:unified"

        cached_data = cache.get_json(cache_key)
        if cached_data:
            data = UnifiedFundamentalsData(**cached_data)
            return UnifiedFundamentalsResponse(
                symbol=resolved.canonical,
                data=data,
                metadata=MultiSourceMetadata(
                    sources={"all": "cache"},
                    cached=True,
                    successful_providers=["cache"]
                )
            )

        data, meta = self.fallback.get_fundamentals_with_fallback(resolved)
        if not data:
            raise ProviderError("fundamentals", f"Unable to fetch fundamentals for {symbol_input}")

        cache.set_json(cache_key, data.model_dump(), ttl=settings.CACHE_FUNDAMENTALS_TTL)

        return UnifiedFundamentalsResponse(
            symbol=resolved.canonical,
            data=data,
            metadata=meta
        )

    def get_income_statement(self, symbol_input: str) -> FinancialStatementResponse:
        t0 = time.monotonic()
        resolved = SymbolResolver.resolve(symbol_input)
        cache_key = f"fundamentals:{resolved.canonical}:income_statement"

        cached_data = cache.get_json(cache_key)
        if cached_data:
            stmt = FinancialStatementData(**cached_data)
            return FinancialStatementResponse(
                symbol=resolved.canonical,
                statement_type="income_statement",
                data=stmt,
                metadata=ResponseMetadata(source="cache", cached=True, latency_ms=(time.monotonic() - t0) * 1000)
            )

        if resolved.country == "IN":
            res = self.screener.get_statement(resolved.symbol, "profit-loss")
            if res.success and res.data:
                cache.set_json(cache_key, res.data.model_dump(), ttl=settings.CACHE_FUNDAMENTALS_TTL)
                return FinancialStatementResponse(
                    symbol=resolved.canonical,
                    statement_type="income_statement",
                    data=res.data,
                    metadata=ResponseMetadata(source=self.screener.name, cached=False, latency_ms=(time.monotonic() - t0) * 1000)
                )

        yf_res = self.yf.get_income_statement(resolved.canonical)
        if yf_res.success and yf_res.data:
            cache.set_json(cache_key, yf_res.data.model_dump(), ttl=settings.CACHE_FUNDAMENTALS_TTL)
            return FinancialStatementResponse(
                symbol=resolved.canonical,
                statement_type="income_statement",
                data=yf_res.data,
                metadata=ResponseMetadata(source=self.yf.name, cached=False, latency_ms=(time.monotonic() - t0) * 1000)
            )

        raise ProviderError("fundamentals", f"Failed to retrieve income statement for {symbol_input}")

    def get_balance_sheet(self, symbol_input: str) -> FinancialStatementResponse:
        t0 = time.monotonic()
        resolved = SymbolResolver.resolve(symbol_input)
        cache_key = f"fundamentals:{resolved.canonical}:balance_sheet"

        cached_data = cache.get_json(cache_key)
        if cached_data:
            stmt = FinancialStatementData(**cached_data)
            return FinancialStatementResponse(
                symbol=resolved.canonical,
                statement_type="balance_sheet",
                data=stmt,
                metadata=ResponseMetadata(source="cache", cached=True, latency_ms=(time.monotonic() - t0) * 1000)
            )

        if resolved.country == "IN":
            res = self.screener.get_statement(resolved.symbol, "balance-sheet")
            if res.success and res.data:
                cache.set_json(cache_key, res.data.model_dump(), ttl=settings.CACHE_FUNDAMENTALS_TTL)
                return FinancialStatementResponse(
                    symbol=resolved.canonical,
                    statement_type="balance_sheet",
                    data=res.data,
                    metadata=ResponseMetadata(source=self.screener.name, cached=False, latency_ms=(time.monotonic() - t0) * 1000)
                )

        yf_res = self.yf.get_balance_sheet(resolved.canonical)
        if yf_res.success and yf_res.data:
            cache.set_json(cache_key, yf_res.data.model_dump(), ttl=settings.CACHE_FUNDAMENTALS_TTL)
            return FinancialStatementResponse(
                symbol=resolved.canonical,
                statement_type="balance_sheet",
                data=yf_res.data,
                metadata=ResponseMetadata(source=self.yf.name, cached=False, latency_ms=(time.monotonic() - t0) * 1000)
            )

        raise ProviderError("fundamentals", f"Failed to retrieve balance sheet for {symbol_input}")

    def get_cash_flow(self, symbol_input: str) -> FinancialStatementResponse:
        t0 = time.monotonic()
        resolved = SymbolResolver.resolve(symbol_input)
        cache_key = f"fundamentals:{resolved.canonical}:cash_flow"

        cached_data = cache.get_json(cache_key)
        if cached_data:
            stmt = FinancialStatementData(**cached_data)
            return FinancialStatementResponse(
                symbol=resolved.canonical,
                statement_type="cash_flow",
                data=stmt,
                metadata=ResponseMetadata(source="cache", cached=True, latency_ms=(time.monotonic() - t0) * 1000)
            )

        if resolved.country == "IN":
            res = self.screener.get_statement(resolved.symbol, "cash-flow")
            if res.success and res.data:
                cache.set_json(cache_key, res.data.model_dump(), ttl=settings.CACHE_FUNDAMENTALS_TTL)
                return FinancialStatementResponse(
                    symbol=resolved.canonical,
                    statement_type="cash_flow",
                    data=res.data,
                    metadata=ResponseMetadata(source=self.screener.name, cached=False, latency_ms=(time.monotonic() - t0) * 1000)
                )

        yf_res = self.yf.get_cash_flow(resolved.canonical)
        if yf_res.success and yf_res.data:
            cache.set_json(cache_key, yf_res.data.model_dump(), ttl=settings.CACHE_FUNDAMENTALS_TTL)
            return FinancialStatementResponse(
                symbol=resolved.canonical,
                statement_type="cash_flow",
                data=yf_res.data,
                metadata=ResponseMetadata(source=self.yf.name, cached=False, latency_ms=(time.monotonic() - t0) * 1000)
            )

        raise ProviderError("fundamentals", f"Failed to retrieve cash flow for {symbol_input}")

    def get_ratios(self, symbol_input: str) -> RatiosResponse:
        t0 = time.monotonic()
        resolved = SymbolResolver.resolve(symbol_input)
        cache_key = f"fundamentals:{resolved.canonical}:ratios"

        cached_data = cache.get_json(cache_key)
        if cached_data:
            ratios = RatiosData(**cached_data)
            return RatiosResponse(
                symbol=resolved.canonical,
                data=ratios,
                metadata=ResponseMetadata(source="cache", cached=True, latency_ms=(time.monotonic() - t0) * 1000)
            )

        if resolved.country == "IN":
            res = self.screener.get_ratios(resolved.symbol)
            if res.success and res.data:
                cache.set_json(cache_key, res.data.model_dump(), ttl=settings.CACHE_FUNDAMENTALS_TTL)
                return RatiosResponse(
                    symbol=resolved.canonical,
                    data=res.data,
                    metadata=ResponseMetadata(source=self.screener.name, cached=False, latency_ms=(time.monotonic() - t0) * 1000)
                )

        yf_info = self.yf.get_info(resolved.canonical)
        if yf_info.success and yf_info.data:
            info = yf_info.data
            ratios = RatiosData(
                pe_ratio=info.get("trailingPE") or info.get("forwardPE"),
                pb_ratio=info.get("priceToBook"),
                roe=info.get("returnOnEquity"),
                debt_to_equity=info.get("debtToEquity"),
                dividend_yield=info.get("dividendYield"),
                book_value=info.get("bookValue"),
                market_cap=info.get("marketCap"),
                current_price=info.get("currentPrice") or info.get("regularMarketPrice")
            )
            cache.set_json(cache_key, ratios.model_dump(), ttl=settings.CACHE_FUNDAMENTALS_TTL)
            return RatiosResponse(
                symbol=resolved.canonical,
                data=ratios,
                metadata=ResponseMetadata(source=self.yf.name, cached=False, latency_ms=(time.monotonic() - t0) * 1000)
            )

        raise ProviderError("fundamentals", f"Failed to retrieve ratios for {symbol_input}")

    def get_shareholding(self, symbol_input: str) -> ShareholdingResponse:
        t0 = time.monotonic()
        resolved = SymbolResolver.resolve(symbol_input)
        cache_key = f"fundamentals:{resolved.canonical}:shareholding"

        cached_data = cache.get_json(cache_key)
        if cached_data:
            return ShareholdingResponse(**cached_data)

        if resolved.country == "IN":
            res = self.screener.get_shareholding(resolved.symbol)
            if res.success and res.data:
                cache.set_json(cache_key, res.data.model_dump(), ttl=settings.CACHE_FUNDAMENTALS_TTL)
                return res.data

        raise ProviderError("fundamentals", f"Shareholding pattern not available for {symbol_input}")

    # --- Extended Fundamentals Features ---

    def get_holders(self, symbol_input: str, holder_type: str = "institutional") -> HoldersResponse:
        resolved = SymbolResolver.resolve(symbol_input)
        res = self.yf.get_holders(resolved.canonical, holder_type=holder_type)
        if not res.success or res.data is None:
            raise ProviderError("yfinance", res.error or f"Failed to retrieve {holder_type} holders")
        return res.data

    def get_insider_transactions(self, symbol_input: str) -> InsiderTransactionsResponse:
        resolved = SymbolResolver.resolve(symbol_input)
        res = self.yf.get_insider_transactions(resolved.canonical)
        if not res.success or res.data is None:
            raise ProviderError("yfinance", res.error or "Failed to retrieve insider transactions")
        return res.data

    def get_sustainability(self, symbol_input: str) -> SustainabilityResponse:
        resolved = SymbolResolver.resolve(symbol_input)
        res = self.yf.get_sustainability(resolved.canonical)
        if not res.success or res.data is None:
            raise ProviderError("yfinance", res.error or "Failed to retrieve sustainability data")
        return res.data

    def get_peers(self, symbol_input: str) -> PeersResponse:
        resolved = SymbolResolver.resolve(symbol_input)
        if resolved.country == "IN":
            res = self.screener.get_peers(resolved.symbol)
            if res.success and res.data:
                return res.data
        raise ProviderError("screener", f"Peers comparison not available for {symbol_input}")

    def get_analysis(self, symbol_input: str) -> CorporateAnalysisResponse:
        resolved = SymbolResolver.resolve(symbol_input)
        if resolved.country == "IN":
            res = self.screener.get_analysis(resolved.symbol)
            if res.success and res.data:
                return res.data
        raise ProviderError("screener", f"Corporate analysis pros/cons not available for {symbol_input}")

    def get_documents(self, symbol_input: str, limit: int = 20) -> DocumentsResponse:
        resolved = SymbolResolver.resolve(symbol_input)
        if resolved.country == "IN":
            res = self.screener.get_documents(resolved.symbol, limit=limit)
            if res.success and res.data:
                return res.data
        raise ProviderError("screener", f"Corporate filings/transcripts not available for {symbol_input}")

