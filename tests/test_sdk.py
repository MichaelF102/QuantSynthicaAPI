import pytest
from fastapi.testclient import TestClient
from quant_synthica_api.main import app

from quantsynthica import QuantSynthica
from quantsynthica.exceptions import NotFoundError, AuthenticationError


@pytest.fixture
def sdk_client():
    # In-memory TestClient for sync test execution
    http_client = TestClient(app)
    client = QuantSynthica(
        api_key="dev_test_api_key_12345",
        base_url="http://testserver",
        http_client=http_client,
    )
    yield client
    client.close()



def test_sdk_health(sdk_client):
    res = sdk_client.stocks.health()
    assert res.status == "healthy"
    assert res.version == "1.0.0"


def test_sdk_market_quote(sdk_client):
    quote = sdk_client.market.get_quote("RELIANCE")
    assert quote.data.symbol == "RELIANCE.NS"
    assert quote.data.price is not None
    # Test dot-access and dict-access both work
    assert quote["data"]["price"] == quote.data.price


def test_sdk_valuation_overview(sdk_client):
    val = sdk_client.valuation.get_overview("RELIANCE")
    assert val.symbol == "RELIANCE.NS"
    assert val.dcf_model.fair_value_per_share > 0
    assert val.piotroski_f_score.f_score >= 0


def test_sdk_sentiment_analyze_text(sdk_client):
    res = sdk_client.sentiment.analyze_text("Quarterly profits surge 40% after record dividend announcement.")
    assert res.label == "Bullish"
    assert res.compound_score > 0


def test_sdk_portfolio_backtest(sdk_client):
    bt = sdk_client.portfolio.backtest(
        symbol="RELIANCE",
        strategy="sma_crossover",
        period="1y",
        params={"fast_period": 10, "slow_period": 25},
    )
    assert bt.strategy == "sma_crossover"
    assert bt.summary.total_return_pct is not None
