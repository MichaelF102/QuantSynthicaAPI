"""Portfolio optimization and algorithmic strategy backtesting resource."""

from typing import List, Optional, Dict, Any
from quantsynthica.resources.base import BaseResource, DotDict


class PortfolioResource(BaseResource):
    def optimize(
        self,
        symbols: List[str],
        objective: str = "max_sharpe",
        period: str = "1y",
        risk_free_rate: float = 0.05,
        target_return: Optional[float] = None,
        include_frontier: bool = False,
    ) -> DotDict:
        """Perform Markowitz Modern Portfolio Theory (MPT) optimization."""
        payload = {
            "symbols": symbols,
            "objective": objective,
            "period": period,
            "risk_free_rate": risk_free_rate,
            "target_return": target_return,
            "include_frontier": include_frontier,
        }
        return self._request("POST", "portfolio/optimize", json_data=payload)

    def analytics(
        self,
        symbols: List[str],
        period: str = "1y",
        risk_free_rate: float = 0.05,
    ) -> DotDict:
        """Get multi-asset correlation matrix, covariance matrix, and portfolio risk."""
        payload = {
            "symbols": symbols,
            "objective": "min_volatility",
            "period": period,
            "risk_free_rate": risk_free_rate,
        }
        return self._request("POST", "portfolio/analytics", json_data=payload)

    def backtest(
        self,
        symbol: str,
        strategy: str = "sma_crossover",
        period: str = "2y",
        params: Optional[Dict[str, Any]] = None,
        initial_capital: float = 100000.0,
        commission_pct: float = 0.001,
        slippage_pct: float = 0.0005,
    ) -> DotDict:
        """Run algorithmic strategy backtest on historical OHLCV data."""
        payload = {
            "symbol": symbol,
            "strategy": strategy,
            "period": period,
            "params": params or {},
            "initial_capital": initial_capital,
            "commission_pct": commission_pct,
            "slippage_pct": slippage_pct,
        }
        return self._request("POST", "portfolio/backtest", json_data=payload)
