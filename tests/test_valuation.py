"""Tests for Valuation models and endpoints."""

import pytest
from fastapi.testclient import TestClient
from quant_synthica_api.main import app
from quant_synthica_api.quant.valuation import (
    calculate_dcf,
    calculate_piotroski_f_score,
    calculate_altman_z_score,
    calculate_graham_valuation,
)

client = TestClient(app)
API_KEY_HEADER = {"X-API-Key": "dev_test_api_key_12345"}


def test_calculate_dcf_basic():
    res = calculate_dcf(
        free_cash_flow=1000.0,
        growth_rate=0.10,
        discount_rate=0.10,
        terminal_growth_rate=0.03,
        years=5,
        net_debt=500.0,
        shares_outstanding=100.0,
        current_price=120.0,
    )
    assert res["starting_fcf"] == 1000.0
    assert len(res["projections"]) == 5
    assert res["enterprise_value"] > 0
    assert res["equity_value"] > 0
    assert res["fair_value_per_share"] > 0
    assert res["margin_of_safety_pct"] is not None


def test_calculate_piotroski_f_score():
    res = calculate_piotroski_f_score(
        net_income_curr=150.0,
        net_income_prev=100.0,
        cfo_curr=200.0,
        roa_curr=0.15,
        roa_prev=0.10,
        long_term_debt_curr=50.0,
        long_term_debt_prev=60.0,
        current_ratio_curr=2.0,
        current_ratio_prev=1.8,
        shares_curr=100.0,
        shares_prev=100.0,
        gross_margin_curr=0.35,
        gross_margin_prev=0.30,
        asset_turnover_curr=1.2,
        asset_turnover_prev=1.1,
    )
    assert res["f_score"] == 9
    assert res["rating"] == "Very Strong"
    assert res["profitability_score"] == 4
    assert res["leverage_liquidity_score"] == 3
    assert res["operating_efficiency_score"] == 2


def test_calculate_altman_z_score():
    res = calculate_altman_z_score(
        working_capital=2000.0,
        total_assets=10000.0,
        retained_earnings=3000.0,
        ebit=1500.0,
        market_cap=25000.0,
        total_liabilities=5000.0,
        sales=12000.0,
        is_manufacturing=True,
    )
    assert res["z_score"] > 3.0
    assert res["zone"] == "Safe Zone"


def test_calculate_graham_valuation():
    res = calculate_graham_valuation(
        eps=10.0,
        book_value_per_share=100.0,
        current_price=120.0,
        current_assets=5000.0,
        total_liabilities=2000.0,
        shares_outstanding=50.0,
    )
    assert res["graham_number"] == 150.0
    assert res["is_undervalued_graham"] is True
    assert res["graham_margin_of_safety_pct"] == 20.0


def test_api_valuation_overview():
    resp = client.get("/api/v1/valuation/RELIANCE", headers=API_KEY_HEADER)
    assert resp.status_code == 200
    data = resp.json()
    assert "symbol" in data
    assert "dcf_model" in data
    assert "piotroski_f_score" in data
    assert "altman_z_score" in data
    assert "graham_valuation" in data


def test_api_valuation_dcf_custom():
    payload = {
        "symbol": "TCS",
        "growth_rate": 0.15,
        "discount_rate": 0.11,
        "terminal_growth_rate": 0.03,
        "years": 5,
    }
    resp = client.post("/api/v1/valuation/dcf", json=payload, headers=API_KEY_HEADER)
    assert resp.status_code == 200
    data = resp.json()
    assert data["assumptions"]["growth_rate_pct"] == 15.0
    assert data["fair_value_per_share"] > 0
