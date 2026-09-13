import pytest
from quant_synthica_api.providers.yfinance_provider import YFinanceProvider

def test_yfinance_provider_quote():
    provider = YFinanceProvider()
    assert provider.health_check() is True
    res = provider.get_quote("RELIANCE.NS")
    assert res.success is True
    assert res.data is not None
    assert res.data.symbol == "RELIANCE.NS"
    assert res.data.price is not None
    assert res.data.price > 0

def test_yfinance_provider_history():
    provider = YFinanceProvider()
    res = provider.get_history("RELIANCE.NS", period="5d", interval="1d")
    assert res.success is True
    assert res.data is not None
    assert len(res.data) > 0
    assert res.data[-1].close > 0

def test_yfinance_provider_dividends():
    provider = YFinanceProvider()
    res = provider.get_dividends("RELIANCE.NS")
    assert res.success is True
    assert res.data is not None

def test_yfinance_provider_financials():
    provider = YFinanceProvider()
    res = provider.get_income_statement("RELIANCE.NS")
    assert res.success is True
    assert res.data is not None
