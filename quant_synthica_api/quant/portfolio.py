"""Portfolio quantitative analytics and Modern Portfolio Theory (MPT) optimization.

Includes:
- Maximum Sharpe Ratio portfolio
- Minimum Volatility portfolio
- Markowitz Efficient Frontier generation
- Covariance and Correlation matrices
- Portfolio Value at Risk (VaR) and Conditional VaR (CVaR)
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import minimize


def portfolio_performance(
    weights: np.ndarray,
    mean_returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float = 0.05,
    periods_per_year: int = 252,
) -> Tuple[float, float, float]:
    """Calculate annualized expected portfolio return, annualized volatility, and Sharpe ratio."""
    p_return = np.sum(mean_returns * weights) * periods_per_year
    p_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix * periods_per_year, weights)))
    sharpe = (p_return - risk_free_rate) / p_vol if p_vol > 0 else 0.0
    return float(p_return), float(p_vol), float(sharpe)


def optimize_portfolio(
    returns_df: pd.DataFrame,
    risk_free_rate: float = 0.05,
    objective: str = "max_sharpe",
    target_return: Optional[float] = None,
    allow_short: bool = False,
) -> Dict[str, Any]:
    """Optimize portfolio weights using Scipy SQSLP solver.

    Args:
        returns_df: DataFrame of daily/periodic returns where each column is an asset.
        risk_free_rate: Annual risk-free rate (e.g. 0.05 for 5%).
        objective: 'max_sharpe', 'min_volatility', or 'efficient_frontier'.
        target_return: Annual target return for constrained optimization.
        allow_short: Whether negative weights are allowed (default False).

    Returns:
        Dictionary containing optimal weights, portfolio return, volatility, Sharpe ratio,
        and asset metrics.
    """
    assets = list(returns_df.columns)
    num_assets = len(assets)
    if num_assets < 2:
        raise ValueError("Portfolio optimization requires at least 2 distinct assets.")

    mean_returns = returns_df.mean().values
    cov_matrix = returns_df.cov().values
    corr_matrix = returns_df.corr().values

    # Initial guess: equal weight
    init_weights = np.ones(num_assets) / num_assets

    # Bounds
    if allow_short:
        bounds = tuple((-1.0, 1.0) for _ in range(num_assets))
    else:
        bounds = tuple((0.0, 1.0) for _ in range(num_assets))

    # Constraint: sum of weights = 1
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]

    if objective == "max_sharpe":
        def neg_sharpe(weights: np.ndarray) -> float:
            _, _, s = portfolio_performance(weights, mean_returns, cov_matrix, risk_free_rate)
            return -s

        res = minimize(neg_sharpe, init_weights, method="SLSQP", bounds=bounds, constraints=constraints)
        opt_weights = res.x

    elif objective == "min_volatility":
        def min_vol(weights: np.ndarray) -> float:
            _, vol, _ = portfolio_performance(weights, mean_returns, cov_matrix, risk_free_rate)
            return vol

        res = minimize(min_vol, init_weights, method="SLSQP", bounds=bounds, constraints=constraints)
        opt_weights = res.x

    elif objective == "target_return" and target_return is not None:
        def min_vol(weights: np.ndarray) -> float:
            _, vol, _ = portfolio_performance(weights, mean_returns, cov_matrix, risk_free_rate)
            return vol

        ret_constraint = {
            "type": "eq",
            "fun": lambda w: (np.sum(mean_returns * w) * 252) - target_return
        }
        constraints.append(ret_constraint)
        res = minimize(min_vol, init_weights, method="SLSQP", bounds=bounds, constraints=constraints)
        opt_weights = res.x if res.success else init_weights
    else:
        # Default to max sharpe
        def neg_sharpe(weights: np.ndarray) -> float:
            _, _, s = portfolio_performance(weights, mean_returns, cov_matrix, risk_free_rate)
            return -s

        res = minimize(neg_sharpe, init_weights, method="SLSQP", bounds=bounds, constraints=constraints)
        opt_weights = res.x

    # Normalize small precision issues
    opt_weights = np.clip(opt_weights, 0.0 if not allow_short else -1.0, 1.0)
    opt_weights = opt_weights / np.sum(opt_weights)

    opt_ret, opt_vol, opt_sharpe = portfolio_performance(opt_weights, mean_returns, cov_matrix, risk_free_rate)

    # Compute portfolio historical return series
    port_daily_returns = (returns_df.values @ opt_weights)
    var_95 = float(np.percentile(port_daily_returns, 5))
    cvar_95 = float(port_daily_returns[port_daily_returns <= var_95].mean()) if len(port_daily_returns[port_daily_returns <= var_95]) > 0 else var_95

    # Individual asset stats
    asset_stats = []
    for i, asset in enumerate(assets):
        ann_ret = float(mean_returns[i] * 252)
        ann_vol = float(np.sqrt(cov_matrix[i, i] * 252))
        sh = float((ann_ret - risk_free_rate) / ann_vol) if ann_vol > 0 else 0.0
        asset_stats.append({
            "symbol": asset,
            "weight": round(float(opt_weights[i]), 4),
            "weight_pct": round(float(opt_weights[i]) * 100, 2),
            "expected_annual_return": round(ann_ret, 4),
            "annual_volatility": round(ann_vol, 4),
            "sharpe_ratio": round(sh, 4),
        })

    # Correlation matrix format
    corr_dict = {}
    for i, a1 in enumerate(assets):
        corr_dict[a1] = {}
        for j, a2 in enumerate(assets):
            corr_dict[a1][a2] = round(float(corr_matrix[i, j]), 4)

    return {
        "objective": objective,
        "optimal_portfolio": {
            "expected_annual_return": round(opt_ret, 4),
            "expected_annual_return_pct": round(opt_ret * 100, 2),
            "annual_volatility": round(opt_vol, 4),
            "annual_volatility_pct": round(opt_vol * 100, 2),
            "sharpe_ratio": round(opt_sharpe, 4),
            "daily_var_95_pct": round(var_95 * 100, 2),
            "daily_cvar_95_pct": round(cvar_95 * 100, 2),
        },
        "allocations": asset_stats,
        "correlation_matrix": corr_dict,
        "risk_free_rate": risk_free_rate,
    }


def generate_efficient_frontier(
    returns_df: pd.DataFrame,
    num_points: int = 20,
    risk_free_rate: float = 0.05,
) -> List[Dict[str, Any]]:
    """Generate points along the Markowitz Efficient Frontier."""
    assets = list(returns_df.columns)
    mean_returns = returns_df.mean().values * 252
    min_ret = float(mean_returns.min())
    max_ret = float(mean_returns.max())

    if min_ret >= max_ret:
        max_ret = min_ret + 0.1

    target_returns = np.linspace(min_ret, max_ret, num_points)
    frontier_points = []

    for tr in target_returns:
        try:
            opt = optimize_portfolio(
                returns_df,
                risk_free_rate=risk_free_rate,
                objective="target_return",
                target_return=float(tr),
            )
            p = opt["optimal_portfolio"]
            frontier_points.append({
                "target_return": round(float(tr), 4),
                "expected_return": p["expected_annual_return"],
                "volatility": p["annual_volatility"],
                "sharpe_ratio": p["sharpe_ratio"],
            })
        except Exception:
            continue

    return frontier_points
