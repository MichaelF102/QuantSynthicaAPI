"""Tests for Financial Sentiment & NLP engine and endpoints."""

import pytest
from fastapi.testclient import TestClient
from quant_synthica_api.main import app
from quant_synthica_api.quant.sentiment import analyze_financial_sentiment

client = TestClient(app)
API_KEY_HEADER = {"X-API-Key": "dev_test_api_key_12345"}


def test_analyze_financial_sentiment_bullish():
    res = analyze_financial_sentiment("Company reports record profit, surges 15% and upgrades annual guidance.")
    assert res["compound_score"] > 0
    assert res["label"] == "Bullish"
    assert "surge" in res["detected_keywords"] or "surges" in res["detected_keywords"] or "profit" in res["detected_keywords"]


def test_analyze_financial_sentiment_bearish():
    res = analyze_financial_sentiment("Shares plunge 25% following fraud investigation, debt default, and dividend cut.")
    assert res["compound_score"] < 0
    assert res["label"] == "Bearish"
    assert any(k in res["detected_keywords"] for k in ["plunge", "fraud", "default", "debt"])


def test_api_sentiment_analyze_text():
    payload = {"text": "Quarterly earnings beat analyst consensus by 12% driven by cloud growth."}
    resp = client.post("/api/v1/sentiment/analyze", json=payload, headers=API_KEY_HEADER)
    assert resp.status_code == 200
    data = resp.json()
    assert data["compound_score"] > 0
    assert data["label"] == "Bullish"


def test_api_symbol_news_sentiment():
    resp = client.get("/api/v1/sentiment/RELIANCE", headers=API_KEY_HEADER)
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_sentiment" in data
    assert "mean_compound_score" in data
    assert "breakdown" in data
