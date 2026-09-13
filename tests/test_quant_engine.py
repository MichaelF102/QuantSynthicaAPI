import pytest
from quant_synthica_api.schemas.market import OHLCVItem
from quant_synthica_api.quant.engine import QuantEngine

def _generate_synthetic_ohlcv(n=50, start_price=100.0, trend=0.002):
    items = []
    p = start_price
    for i in range(n):
        open_p = p
        change = (i % 5 - 2) * 0.5 + trend * p
        close_p = open_p + change
        high_p = max(open_p, close_p) + 0.5
        low_p = min(open_p, close_p) - 0.5
        vol = 1000 + i * 10
        items.append(OHLCVItem(
            date=f"2024-01-{(i+1):02d}" if (i+1) <= 31 else f"2024-02-{(i-30):02d}",
            open=round(open_p, 2),
            high=round(high_p, 2),
            low=round(low_p, 2),
            close=round(close_p, 2),
            adj_close=round(close_p, 2),
            volume=vol
        ))
        p = close_p
    return items

def test_quant_engine_returns():
    items = _generate_synthetic_ohlcv(60)
    ret = QuantEngine.compute_returns(items, "TEST.NS")
    assert ret.symbol == "TEST.NS"
    assert ret.daily_return is not None
    assert ret.cumulative_return is not None

def test_quant_engine_risk():
    items = _generate_synthetic_ohlcv(60)
    risk = QuantEngine.compute_risk(items, "TEST.NS")
    assert risk.annualized_volatility is not None
    assert risk.annualized_volatility > 0
    assert risk.sharpe_ratio is not None
    assert risk.max_drawdown is not None
    assert risk.max_drawdown <= 0.0

def test_quant_engine_technical():
    items = _generate_synthetic_ohlcv(60)
    tech = QuantEngine.compute_technical(items, "TEST.NS")
    assert tech.last_price == items[-1].close
    assert tech.sma_20 is not None
    assert tech.sma_50 is not None
    assert tech.rsi_14 is not None
    assert 0 <= tech.rsi_14 <= 100
    assert tech.bollinger_upper is not None
    assert tech.bollinger_lower is not None
    assert tech.bollinger_upper >= tech.bollinger_lower
