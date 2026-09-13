import pytest
from fastapi.testclient import TestClient

def test_screener_crypto(client: TestClient):
    res = client.post("/api/v1/screener/crypto", json={"limit": 2})
    assert res.status_code == 200
    data = res.json()
    assert data["asset_class"] == "crypto"
    assert len(data["items"]) <= 2

def test_screener_forex(client: TestClient):
    res = client.post("/api/v1/screener/forex", json={"limit": 2})
    assert res.status_code == 200
    data = res.json()
    assert data["asset_class"] == "forex"
    assert len(data["items"]) <= 2

def test_screener_bonds(client: TestClient):
    res = client.post("/api/v1/screener/bonds", json={"limit": 2})
    assert res.status_code == 200
    data = res.json()
    assert data["asset_class"] == "bonds"

def test_market_recommendations(client: TestClient):
    res = client.get("/api/v1/market/AAPL/recommendations")
    assert res.status_code == 200
    data = res.json()
    assert data["symbol"] == "AAPL"
    assert data["metadata"]["source"] == "yfinance"

def test_market_options_chain(client: TestClient):
    res = client.get("/api/v1/market/AAPL/options")
    assert res.status_code == 200
    data = res.json()
    assert data["symbol"] == "AAPL"
    assert "calls" in data
    assert "puts" in data

def test_market_news(client: TestClient):
    res = client.get("/api/v1/market/AAPL/news")
    assert res.status_code == 200
    data = res.json()
    assert "news" in data
    assert data["count"] > 0

def test_institutional_holders(client: TestClient):
    res = client.get("/api/v1/fundamentals/AAPL/institutional-holders")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "institutional"
    assert len(data["holders"]) > 0

def test_screener_peers(client: TestClient):
    res = client.get("/api/v1/fundamentals/RELIANCE/peers")
    assert res.status_code == 200
    data = res.json()
    assert len(data["peers"]) > 0

def test_screener_analysis(client: TestClient):
    res = client.get("/api/v1/fundamentals/RELIANCE/analysis")
    assert res.status_code == 200
    data = res.json()
    assert "pros" in data
    assert "cons" in data

def test_screener_documents(client: TestClient):
    res = client.get("/api/v1/fundamentals/RELIANCE/documents?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] > 0
    assert "url" in data["documents"][0]
