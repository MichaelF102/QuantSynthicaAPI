import pytest
from quant_synthica_api.services.normalization_service import NormalizationService
from quant_synthica_api.schemas.common import ResolvedSymbol
from quant_synthica_api.schemas.market import QuoteData
from quant_synthica_api.schemas.fundamentals import (
    UnifiedFundamentalsData, RatiosData, FinancialStatementData, FinancialRow
)
from quant_synthica_api.schemas.quant import (
    QuantSummaryData, ReturnsMetrics, RiskMetrics, TechnicalIndicators
)

def test_normalization_merges_and_attributes_sources():
    resolved = ResolvedSymbol(
        input="RELIANCE",
        canonical="RELIANCE.NS",
        symbol="RELIANCE",
        exchange="NSE",
        tradingview="NSE:RELIANCE",
        screener="RELIANCE",
        yfinance="RELIANCE.NS",
        country="IN"
    )

    quote = QuoteData(
        symbol="RELIANCE.NS",
        name="Reliance Industries Ltd",
        price=1405.50,
        volume=8234211,
        market_cap=1900000000000.0,
        pe_ratio=25.0
    )

    pl_stmt = FinancialStatementData(
        statement_type="profit-loss",
        periods=["Mar 2023", "Mar 2024"],
        rows=[
            FinancialRow(metric="Sales", values={"Mar 2023": 100.0, "Mar 2024": 115.0}),
            FinancialRow(metric="Net Profit", values={"Mar 2023": 10.0, "Mar 2024": 12.0})
        ]
    )

    fundamentals = UnifiedFundamentalsData(
        symbol="RELIANCE",
        name="Reliance Industries Ltd",
        ratios=RatiosData(
            pe_ratio=24.2,
            pb_ratio=3.1,
            roe=18.5,
            roce=21.1,
            dividend_yield=0.35,
            current_price=1405.0
        ),
        profit_and_loss=pl_stmt
    )

    quant_summary = QuantSummaryData(
        symbol="RELIANCE.NS",
        returns=ReturnsMetrics(symbol="RELIANCE.NS", cagr=0.15, daily_return=0.01),
        risk=RiskMetrics(symbol="RELIANCE.NS", annualized_volatility=0.23, sharpe_ratio=1.21, max_drawdown=-0.18),
        technical=TechnicalIndicators(symbol="RELIANCE.NS", rsi_14=61.2, macd=8.2)
    )

    profile = NormalizationService.build_unified_profile(
        resolved=resolved,
        quote=quote,
        quote_source="yfinance",
        fundamentals=fundamentals,
        fundamentals_source="screener",
        quant_summary=quant_summary,
        quant_source="quant_engine"
    )

    # Check identity
    assert profile.identity.symbol == "RELIANCE"
    assert profile.identity.exchange == "NSE"

    # Check market
    assert profile.market.price == 1405.50
    assert profile.sources["price"] == "yfinance"

    # Check valuation (Screener prioritized for fundamental valuation)
    assert profile.valuation.pe == 24.2
    assert profile.valuation.pb == 3.1
    assert profile.sources["valuation"] == "screener"

    # Check profitability
    assert profile.profitability.roe == 18.5
    assert profile.profitability.roce == 21.1

    # Check growth
    assert profile.growth.revenue_growth == 15.0
    assert profile.growth.profit_growth == 20.0

    # Check quant & technical
    assert profile.technical.rsi == 61.2
    assert profile.quant.volatility == 0.23
    assert profile.quant.sharpe == 1.21
    assert profile.quant.max_drawdown == -0.18
    assert profile.sources["technical"] == "quant_engine"
