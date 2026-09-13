"""Tests for Portfolio Optimization and Strategy Backtesting."""

import pytest
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient
from quant_synthica_api.main import app
from quant_synthica_api.quant.portfolio import optimize_portfolio, generate_efficient_frontier
from quant_synthica_api.quant.backtest import run_strategy_backtest

client = TestClient(app)
API_KEY_HEADER = {"X-API-Key": "dev_test_api_key_12345"}


def test_optimize_portfolio_unit():
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=100, freq="D")
    r1 = np.random.normal(0.0008, 0.015, 100)
    r2 = np.random.normal(0.0005, 0.010, 100)
    r3 = np.random.normal(0.0012, 0.022, 100)
    df = pd.DataFrame({"AAPL": r1, "MSFT": r2, "GOOGL": r3}, index=dates)

    res = optimize_portfolio(df, objective="max_sharpe")
    assert "optimal_portfolio" in res
    assert "allocations" in res
    assert len(res["allocations"]) == 3
    # Weights sum to 1.0
    total_w = sum(a["weight"] for a in res["allocations"])
    assert pytest.approx(total_w, 0.01) == 1.0

    frontier = generate_efficient_frontier(df, num_points=5)
    assert len(frontier) > 0


def test_run_strategy_backtest_unit():
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=120, freq="D")
    # Synthetic trending series
    price = 100.0
    prices = []
    for _ in range(120):
        price += np.random.normal(0.2, 1.0)
        prices.append(max(10.0, price))

    df = pd.DataFrame({
        "date": dates,
        "open": prices,
        "high": [p + 1.0 for p in prices],
        "low": [p - 1.0 for p in prices],
        "close": prices,
        "volume": [100000] * 120,
    })

    res = run_strategy_backtest(df, strategy="sma_crossover", params={"fast_period": 10, "slow_period": 25})
    assert res["strategy"] == "sma_crossover"
    assert "summary" in res
    assert "total_return_pct" in res["summary"]
    assert "equity_curve" in res
    assert len(res["equity_curve"]) > 0


def test_api_portfolio_optimize():
    payload = {
        "symbols": ["RELIANCE", "TCS"],
        "objective": "max_sharpe",
        "period": "6m",
        "include_frontier": True,
    }
    resp = client.post("/api/v1/portfolio/optimize", json=payload, headers=API_KEY_HEADER)
    assert resp.status_code == 200
    data = resp.json()
    assert "optimal_portfolio" in data
    assert "correlation_matrix" in data


def test_api_portfolio_backtest():
    payload = {
        "symbol": "RELIANCE",
        "strategy": "sma_crossover",
        "period": "1y",
        "params": {"fast_period": 10, "slow_period": 30},
        "initial_capital": 50000.0,
    }
    resp = client.post("/api/v1/portfolio/backtest", json=payload, headers=API_KEY_HEADER)
    assert resp.status_code == 200
    data = resp.json()
    assert data["strategy"] == "sma_crossover"
    assert "summary" in data
    assert "trades" in data
