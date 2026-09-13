import pytest
from quant_synthica_api.services.symbol_resolver import SymbolResolver
from quant_synthica_api.core.exceptions import SymbolResolutionError

def test_resolve_nse_symbol():
    res = SymbolResolver.resolve("RELIANCE")
    assert res.canonical == "RELIANCE.NS"
    assert res.symbol == "RELIANCE"
    assert res.exchange == "NSE"
    assert res.tradingview == "NSE:RELIANCE"
    assert res.screener == "RELIANCE"
    assert res.country == "IN"

def test_resolve_canonical_input():
    res = SymbolResolver.resolve("RELIANCE.NS")
    assert res.canonical == "RELIANCE.NS"
    assert res.nse == "RELIANCE"
    assert res.bse == "500325"

def test_resolve_bse_symbol():
    res = SymbolResolver.resolve("RELIANCE.BO")
    assert res.canonical == "RELIANCE.BO"
    assert res.exchange == "BSE"
    assert res.tradingview == "BSE:RELIANCE"

def test_resolve_bse_numerical_code():
    res = SymbolResolver.resolve("500325")
    assert res.symbol == "RELIANCE"
    assert res.canonical == "RELIANCE.NS"

def test_resolve_us_symbol():
    res = SymbolResolver.resolve("NASDAQ:AAPL")
    assert res.canonical == "AAPL"
    assert res.symbol == "AAPL"
    assert res.exchange == "NASDAQ"
    assert res.country == "US"

def test_empty_symbol_fails():
    with pytest.raises(SymbolResolutionError):
        SymbolResolver.resolve("")
