import time
from typing import Optional, Tuple, Dict, Any, List
from quant_synthica_api.providers.yfinance_provider import YFinanceProvider
from quant_synthica_api.providers.screener_provider import ScreenerProvider
from quant_synthica_api.providers.tradingview_provider import TradingViewProvider
from quant_synthica_api.schemas.market import QuoteData
from quant_synthica_api.schemas.fundamentals import RatiosData, FinancialStatementData, UnifiedFundamentalsData
from quant_synthica_api.schemas.common import ResolvedSymbol, MultiSourceMetadata
from quant_synthica_api.core.logging import logger

class FallbackService:
    def __init__(
        self,
        yf_provider: YFinanceProvider,
        screener_provider: ScreenerProvider,
        tv_provider: TradingViewProvider
    ):
        self.yf = yf_provider
        self.screener = screener_provider
        self.tv = tv_provider

    def get_quote_with_fallback(
        self, resolved: ResolvedSymbol
    ) -> Tuple[Optional[QuoteData], MultiSourceMetadata]:
        successful: List[str] = []
        failed: List[Dict[str, Any]] = []
        sources: Dict[str, str] = {}

        # 1. Primary: yfinance
        yf_res = self.yf.get_quote(resolved.canonical)
        if yf_res.success and yf_res.data and yf_res.data.price is not None:
            successful.append("yfinance")
            sources["quote"] = "yfinance"
            sources["price"] = "yfinance"
            meta = MultiSourceMetadata(
                sources=sources,
                cached=yf_res.cached,
                successful_providers=successful,
                failed_providers=failed
            )
            return yf_res.data, meta
        else:
            failed.append({
                "provider": "yfinance",
                "error": yf_res.error or "Price unavailable"
            })

        # 2. Fallback: Screener.in (if Indian stock)
        if resolved.country == "IN":
            sc_res = self.screener.get_ratios(resolved.symbol)
            if sc_res.success and sc_res.data and sc_res.data.current_price is not None:
                successful.append("screener")
                sources["quote"] = "screener"
                sources["price"] = "screener"
                quote = QuoteData(
                    symbol=resolved.canonical,
                    name=resolved.symbol,
                    exchange=resolved.exchange,
                    currency="INR",
                    price=sc_res.data.current_price,
                    market_cap=sc_res.data.market_cap,
                    pe_ratio=sc_res.data.pe_ratio,
                    dividend_yield=sc_res.data.dividend_yield,
                    fifty_two_week_high=sc_res.data.high_52w,
                    fifty_two_week_low=sc_res.data.low_52w
                )
                meta = MultiSourceMetadata(
                    sources=sources,
                    cached=sc_res.cached,
                    successful_providers=successful,
                    failed_providers=failed
                )
                return quote, meta
            else:
                failed.append({
                    "provider": "screener",
                    "error": sc_res.error or "Price unavailable"
                })

        meta = MultiSourceMetadata(
            sources=sources,
            cached=False,
            successful_providers=successful,
            failed_providers=failed
        )
        return None, meta

    def get_fundamentals_with_fallback(
        self, resolved: ResolvedSymbol
    ) -> Tuple[Optional[UnifiedFundamentalsData], MultiSourceMetadata]:
        successful: List[str] = []
        failed: List[Dict[str, Any]] = []
        sources: Dict[str, str] = {}

        # 1. Primary for fundamentals: Screener.in (if Indian stock)
        if resolved.country == "IN":
            sc_res = self.screener.get_company_profile(resolved.symbol)
            if sc_res.success and sc_res.data:
                successful.append("screener")
                sources["fundamentals"] = "screener"
                meta = MultiSourceMetadata(
                    sources=sources,
                    cached=sc_res.cached,
                    successful_providers=successful,
                    failed_providers=failed
                )
                return sc_res.data, meta
            else:
                failed.append({
                    "provider": "screener",
                    "error": sc_res.error or "Screener.in fundamentals failed"
                })

        # 2. Fallback: yfinance financial statements & ratios
        yf_info = self.yf.get_info(resolved.canonical)
        if yf_info.success and yf_info.data:
            successful.append("yfinance")
            sources["fundamentals"] = "yfinance"
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
            income_res = self.yf.get_income_statement(resolved.canonical)
            bs_res = self.yf.get_balance_sheet(resolved.canonical)
            cf_res = self.yf.get_cash_flow(resolved.canonical)

            data = UnifiedFundamentalsData(
                symbol=resolved.symbol,
                name=info.get("shortName") or info.get("longName") or resolved.symbol,
                about=info.get("longBusinessSummary"),
                ratios=ratios,
                profit_and_loss=income_res.data if income_res.success else None,
                balance_sheet=bs_res.data if bs_res.success else None,
                cash_flow=cf_res.data if cf_res.success else None
            )
            meta = MultiSourceMetadata(
                sources=sources,
                cached=yf_info.cached,
                successful_providers=successful,
                failed_providers=failed
            )
            return data, meta
        else:
            failed.append({
                "provider": "yfinance",
                "error": yf_info.error or "yfinance fundamentals unavailable"
            })

        meta = MultiSourceMetadata(
            sources=sources,
            cached=False,
            successful_providers=successful,
            failed_providers=failed
        )
        return None, meta
