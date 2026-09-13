"""Portfolio and Backtesting service."""

import time
from typing import List, Dict, Any, Optional
import pandas as pd

from quant_synthica_api.core.config import get_settings
from quant_synthica_api.core.exceptions import ProviderError
from quant_synthica_api.services.symbol_resolver import SymbolResolver
from quant_synthica_api.services.market_service import MarketService
from quant_synthica_api.quant.portfolio import optimize_portfolio, generate_efficient_frontier
from quant_synthica_api.quant.backtest import run_strategy_backtest

settings = get_settings()


class PortfolioService:
    def __init__(self, market_service: MarketService):
        self.market = market_service

    def _normalize_period(self, period: str) -> str:
        p = period.lower().strip()
        period_map = {"1m": "1mo", "3m": "3mo", "6m": "6mo"}
        return period_map.get(p, p)

    def _get_returns_matrix(self, symbols: List[str], period: str = "1y") -> pd.DataFrame:
        """Fetch historical close prices and build returns dataframe."""
        norm_period = self._normalize_period(period)
        all_series = {}
        for s in symbols:
            resolved = SymbolResolver.resolve(s)
            hist = self.market.get_history(resolved.canonical, period=norm_period, interval="1d")

            if not hist.data or len(hist.data) < 10:
                continue
            dates = [item.date for item in hist.data]
            closes = [float(item.close) for item in hist.data]
            s_series = pd.Series(closes, index=pd.to_datetime(dates)).pct_change().dropna()
            all_series[resolved.canonical] = s_series

        if len(all_series) < 2:
            raise ProviderError("portfolio", "At least 2 symbols with valid historical data are required.")

        returns_df = pd.DataFrame(all_series).dropna()
        if len(returns_df) < 10:
            raise ProviderError("portfolio", "Insufficient overlapping price history for symbols.")
        return returns_df

    def optimize(
        self,
        symbols: List[str],
        objective: str = "max_sharpe",
        period: str = "1y",
        risk_free_rate: float = 0.05,
        target_return: Optional[float] = None,
        include_frontier: bool = False,
    ) -> Dict[str, Any]:
        """Perform portfolio optimization."""
        t0 = time.monotonic()
        returns_df = self._get_returns_matrix(symbols, period=period)
        opt_res = optimize_portfolio(
            returns_df,
            risk_free_rate=risk_free_rate,
            objective=objective,
            target_return=target_return,
        )

        if include_frontier:
            opt_res["efficient_frontier"] = generate_efficient_frontier(
                returns_df, num_points=15, risk_free_rate=risk_free_rate
            )

        opt_res["symbols"] = list(returns_df.columns)
        opt_res["period"] = period
        opt_res["latency_ms"] = round((time.monotonic() - t0) * 1000, 2)
        return opt_res

    def run_backtest(
        self,
        symbol: str,
        strategy: str = "sma_crossover",
        period: str = "2y",
        params: Optional[Dict[str, Any]] = None,
        initial_capital: float = 100000.0,
        commission_pct: float = 0.001,
        slippage_pct: float = 0.0005,
    ) -> Dict[str, Any]:
        """Run backtest simulation for a single asset."""
        t0 = time.monotonic()
        resolved = SymbolResolver.resolve(symbol)
        norm_period = self._normalize_period(period)
        hist = self.market.get_history(resolved.canonical, period=norm_period, interval="1d")

        if not hist.data or len(hist.data) < 30:
            raise ProviderError("backtest", f"Insufficient price history for symbol {symbol} to run backtest.")

        records = [item.model_dump() for item in hist.data]
        df = pd.DataFrame(records)

        result = run_strategy_backtest(
            df=df,
            strategy=strategy,
            params=params,
            initial_capital=initial_capital,
            commission_pct=commission_pct,
            slippage_pct=slippage_pct,
        )

        result["symbol"] = resolved.canonical
        result["period"] = period
        result["latency_ms"] = round((time.monotonic() - t0) * 1000, 2)
        return result
