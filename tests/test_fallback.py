import pytest
from unittest.mock import MagicMock
from quant_synthica_api.providers.base import ProviderResult
from quant_synthica_api.schemas.market import QuoteData
from quant_synthica_api.schemas.fundamentals import RatiosData
from quant_synthica_api.schemas.common import ResolvedSymbol
from quant_synthica_api.services.fallback_service import FallbackService

def test_fallback_service_when_primary_fails():
    mock_yf = MagicMock()
    mock_screener = MagicMock()
    mock_tv = MagicMock()

    # Simulate yfinance failure
    mock_yf.get_quote.return_value = ProviderResult(
        data=None, provider="yfinance", success=False, error="Rate limited"
    )

    # Screener succeeds with fallback price
    mock_screener.get_ratios.return_value = ProviderResult(
        data=RatiosData(current_price=1255.0, market_cap=1700000000000.0),
        provider="screener",
        success=True
    )

    fallback = FallbackService(mock_yf, mock_screener, mock_tv)
    resolved = ResolvedSymbol(
        input="RELIANCE",
        canonical="RELIANCE.NS",
        symbol="RELIANCE",
        exchange="NSE",
        country="IN"
    )

    quote, meta = fallback.get_quote_with_fallback(resolved)
    assert quote is not None
    assert quote.price == 1255.0
    assert "screener" in meta.successful_providers
    assert any(f["provider"] == "yfinance" for f in meta.failed_providers)
