import pytest
from quant_synthica_api.providers.tradingview_provider import TradingViewProvider
from quant_synthica_api.schemas.screener import ScreenerQueryRequest, ScreenerFilter

def test_tradingview_provider_query():
    provider = TradingViewProvider()
    assert provider.health_check() is True

    req = ScreenerQueryRequest(
        market="india",
        exchange="NSE",
        filters=ScreenerFilter(market_cap_min=10000000000),
        limit=5
    )
    res = provider.query_screener(req)
    assert res.success is True
    assert res.data is not None
    assert res.data.total_count > 0
    assert len(res.data.items) <= 5
    assert res.data.items[0].ticker.startswith("NSE:")
