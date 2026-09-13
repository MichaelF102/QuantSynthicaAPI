from typing import Optional, Dict, Any, Tuple
from quant_synthica_api.schemas.stock_profile import (
    StockProfileResponse, StockIdentity, StockMarketMetrics, StockValuationMetrics,
    StockProfitabilityMetrics, StockGrowthMetrics, StockTechnicalMetrics, StockQuantMetrics
)
from quant_synthica_api.schemas.market import QuoteData
from quant_synthica_api.schemas.fundamentals import RatiosData, UnifiedFundamentalsData
from quant_synthica_api.schemas.quant import QuantSummaryData
from quant_synthica_api.schemas.common import ResolvedSymbol

class NormalizationService:
    """
    Normalizes divergent provider fields into unified canonical schema
    and tracks field-level provenance / sources.
    """

    @staticmethod
    def build_unified_profile(
        resolved: ResolvedSymbol,
        quote: Optional[QuoteData] = None,
        quote_source: str = "yfinance",
        fundamentals: Optional[UnifiedFundamentalsData] = None,
        fundamentals_source: str = "screener",
        quant_summary: Optional[QuantSummaryData] = None,
        quant_source: str = "quant_engine"
    ) -> StockProfileResponse:
        sources: Dict[str, str] = {}

        # 1. Identity
        company_name = None
        if fundamentals and fundamentals.name:
            company_name = fundamentals.name
            sources["name"] = fundamentals_source
        elif quote and quote.name:
            company_name = quote.name
            sources["name"] = quote_source
        else:
            company_name = resolved.symbol

        identity = StockIdentity(
            symbol=resolved.symbol,
            name=company_name,
            exchange=resolved.exchange or "NSE",
            currency="INR" if resolved.country == "IN" else "USD",
            country=resolved.country
        )

        # 2. Market Metrics
        # Priority for Market Data: yfinance (live) -> screener
        price = None
        vol = None
        mcap = None
        change_pct = None
        high_52 = None
        low_52 = None

        if quote and quote.price is not None:
            price = quote.price
            vol = float(quote.volume) if quote.volume else None
            mcap = quote.market_cap
            change_pct = quote.change_percent
            high_52 = quote.fifty_two_week_high
            low_52 = quote.fifty_two_week_low
            sources["market"] = quote_source
            sources["price"] = quote_source
        elif fundamentals and fundamentals.ratios:
            r = fundamentals.ratios
            price = r.current_price
            mcap = r.market_cap
            high_52 = r.high_52w
            low_52 = r.low_52w
            sources["market"] = fundamentals_source
            sources["price"] = fundamentals_source

        market = StockMarketMetrics(
            price=price,
            change_percent=change_pct,
            volume=vol,
            market_cap=mcap,
            fifty_two_week_high=high_52,
            fifty_two_week_low=low_52
        )

        # 3. Valuation Metrics
        # Priority: Screener.in -> yfinance
        pe = None
        pb = None
        div_yield = None
        bv = None
        debt_to_eq = None

        if fundamentals and fundamentals.ratios:
            r = fundamentals.ratios
            pe = r.pe_ratio
            pb = r.pb_ratio
            div_yield = r.dividend_yield
            bv = r.book_value
            debt_to_eq = r.debt_to_equity
            sources["valuation"] = fundamentals_source
            sources["pe"] = fundamentals_source
        elif quote:
            pe = quote.pe_ratio
            div_yield = quote.dividend_yield
            sources["valuation"] = quote_source
            sources["pe"] = quote_source

        valuation = StockValuationMetrics(
            pe=pe,
            pb=pb,
            dividend_yield=div_yield,
            book_value=bv,
            debt_to_equity=debt_to_eq
        )

        # 4. Profitability Metrics
        roe = None
        roce = None
        opm = None
        npm = None
        if fundamentals and fundamentals.ratios:
            r = fundamentals.ratios
            roe = r.roe
            roce = r.roce
            sources["profitability"] = fundamentals_source
            sources["roe"] = fundamentals_source
            sources["roce"] = fundamentals_source

        # Extract OPM / NPM from profit_and_loss if available
        if fundamentals and fundamentals.profit_and_loss:
            for row in fundamentals.profit_and_loss.rows:
                metric_clean = row.metric.lower()
                if "opm" in metric_clean or "operating profit margin" in metric_clean:
                    latest_val = next((v for v in reversed(list(row.values.values())) if v is not None), None)
                    if latest_val is not None:
                        opm = latest_val
                elif "net profit" in metric_clean:
                    latest_val = next((v for v in reversed(list(row.values.values())) if v is not None), None)
                    if latest_val is not None:
                        npm = latest_val

        profitability = StockProfitabilityMetrics(
            roe=roe,
            roce=roce,
            opm=opm,
            npm=npm
        )

        # 5. Growth Metrics
        # Calculate revenue & profit growth from P&L if available
        rev_growth = None
        profit_growth = None
        if fundamentals and fundamentals.profit_and_loss:
            pl = fundamentals.profit_and_loss
            sales_row = next((r for r in pl.rows if "sales" in r.metric.lower() or "revenue" in r.metric.lower()), None)
            net_profit_row = next((r for r in pl.rows if "net profit" in r.metric.lower()), None)

            def calc_growth(row):
                if not row:
                    return None
                valid_vals = [v for v in row.values.values() if v is not None and v != 0]
                if len(valid_vals) >= 2:
                    prev = valid_vals[-2]
                    curr = valid_vals[-1]
                    if prev > 0:
                        return round(((curr - prev) / prev) * 100.0, 2)
                return None

            rev_growth = calc_growth(sales_row)
            profit_growth = calc_growth(net_profit_row)
            sources["growth"] = fundamentals_source

        growth = StockGrowthMetrics(
            revenue_growth=rev_growth,
            profit_growth=profit_growth
        )

        # 6. Technical & Quant
        rsi = None
        macd = None
        sma_50 = None
        sma_200 = None
        volatility = None
        sharpe = None
        max_dd = None

        if quant_summary:
            sources["technical"] = quant_source
            sources["quant"] = quant_source
            t = quant_summary.technical
            rsi = t.rsi_14
            macd = t.macd
            sma_50 = t.sma_50
            sma_200 = t.sma_200

            rk = quant_summary.risk
            volatility = rk.annualized_volatility
            sharpe = rk.sharpe_ratio
            max_dd = rk.max_drawdown

        technical = StockTechnicalMetrics(
            rsi=rsi,
            macd=macd,
            sma_50=sma_50,
            sma_200=sma_200
        )

        quant = StockQuantMetrics(
            volatility=volatility,
            sharpe=sharpe,
            max_drawdown=max_dd
        )

        return StockProfileResponse(
            identity=identity,
            market=market,
            valuation=valuation,
            profitability=profitability,
            growth=growth,
            technical=technical,
            quant=quant,
            sources=sources
        )
