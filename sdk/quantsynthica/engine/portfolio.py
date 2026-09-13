"""Portfolio quantitative analytics and Modern Portfolio Theory (MPT) optimization."""

from typing import List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from quantsynthica.resources.base import DotDict


def portfolio_performance(
    weights: np.ndarray,
    mean_returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float = 0.05,
) -> Tuple[float, float, float]:
    p_return = np.sum(mean_returns * weights) * 252
    p_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix * 252, weights)))
    sharpe = (p_return - risk_free_rate) / p_vol if p_vol > 0 else 0.0
    return float(p_return), float(p_vol), float(sharpe)


def optimize_portfolio(
    returns_df: pd.DataFrame,
    risk_free_rate: float = 0.05,
    objective: str = "max_sharpe",
    target_return: Optional[float] = None,
) -> DotDict:
    assets = list(returns_df.columns)
    num_assets = len(assets)
    if num_assets < 2:
        raise ValueError("Portfolio optimization requires at least 2 distinct assets.")

    mean_returns = returns_df.mean().values
    cov_matrix = returns_df.cov().values
    corr_matrix = returns_df.corr().values
    init_weights = np.ones(num_assets) / num_assets
    bounds = tuple((0.0, 1.0) for _ in range(num_assets))
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]

    if objective == "min_volatility":
        def min_vol(w: np.ndarray) -> float:
            _, vol, _ = portfolio_performance(w, mean_returns, cov_matrix, risk_free_rate)
            return vol
        res = minimize(min_vol, init_weights, method="SLSQP", bounds=bounds, constraints=constraints)
    else:  # max_sharpe
        def neg_sharpe(w: np.ndarray) -> float:
            _, _, s = portfolio_performance(w, mean_returns, cov_matrix, risk_free_rate)
            return -s
        res = minimize(neg_sharpe, init_weights, method="SLSQP", bounds=bounds, constraints=constraints)

    opt_weights = np.clip(res.x, 0.0, 1.0)
    opt_weights = opt_weights / np.sum(opt_weights)
    opt_ret, opt_vol, opt_sharpe = portfolio_performance(opt_weights, mean_returns, cov_matrix, risk_free_rate)

    allocations = []
    for i, asset in enumerate(assets):
        allocations.append({
            "symbol": asset,
            "weight": round(float(opt_weights[i]), 4),
            "weight_pct": round(float(opt_weights[i]) * 100, 2),
            "expected_annual_return": round(float(mean_returns[i] * 252), 4),
        })

    corr_dict = {}
    for i, a1 in enumerate(assets):
        corr_dict[a1] = {}
        for j, a2 in enumerate(assets):
            corr_dict[a1][a2] = round(float(corr_matrix[i, j]), 4)

    return DotDict({
        "objective": objective,
        "optimal_portfolio": {
            "expected_annual_return": round(opt_ret, 4),
            "expected_annual_return_pct": round(opt_ret * 100, 2),
            "annual_volatility": round(opt_vol, 4),
            "annual_volatility_pct": round(opt_vol * 100, 2),
            "sharpe_ratio": round(opt_sharpe, 4),
        },
        "allocations": allocations,
        "correlation_matrix": corr_dict,
    })
