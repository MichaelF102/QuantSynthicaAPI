import pytest
from fastapi.testclient import TestClient

def test_health_endpoint(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "providers" in data
    assert data["providers"]["yfinance"] == "healthy"
    assert data["providers"]["tradingview"] == "healthy"
    assert data["providers"]["screener_in"] == "healthy"

def test_search_endpoint(client: TestClient):
    response = client.get("/api/v1/search?q=RELIANCE")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
    assert any(item["symbol"] == "RELIANCE" for item in data["results"])

def test_screener_query_endpoint(client: TestClient):
    payload = {
        "market": "india",
        "exchange": "NSE",
        "filters": {
            "market_cap_min": 10000000000,
            "pe_max": 50
        },
        "limit": 3
    }
    response = client.post("/api/v1/screener/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) <= 3
    assert data["metadata"]["source"] == "tradingview"

def test_screener_predefined_value(client: TestClient):
    response = client.get("/api/v1/screener/value?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data

def test_market_quote_endpoint(client: TestClient):
    response = client.get("/api/v1/market/RELIANCE.NS/quote")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["symbol"] == "RELIANCE.NS"
    assert data["data"]["price"] is not None

def test_market_history_endpoint(client: TestClient):
    response = client.get("/api/v1/market/RELIANCE.NS/history?period=5d&interval=1d")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) > 0
    assert "close" in data["data"][0]

def test_quant_risk_endpoint(client: TestClient):
    response = client.get("/api/v1/quant/RELIANCE.NS/risk?period=3mo")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["annualized_volatility"] is not None

def test_technical_endpoint(client: TestClient):
    response = client.get("/api/v1/technical/RELIANCE.NS?period=3mo")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["last_price"] is not None

def test_fundamentals_endpoint(client: TestClient):
    response = client.get("/api/v1/fundamentals/RELIANCE")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["symbol"] == "RELIANCE"
    assert data["data"]["ratios"] is not None

def test_stocks_profile_endpoint(client: TestClient):
    response = client.get("/api/v1/stocks/RELIANCE")
    assert response.status_code == 200
    data = response.json()
    assert data["identity"]["symbol"] == "RELIANCE"
    assert "market" in data
    assert "valuation" in data
    assert "profitability" in data
    assert "quant" in data
    assert "sources" in data
