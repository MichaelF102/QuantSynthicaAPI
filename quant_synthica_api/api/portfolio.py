"""Portfolio optimization and Algorithmic Strategy Backtesting API endpoints."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from quant_synthica_api.core.security import verify_api_key
from quant_synthica_api.services.container import container
from quant_synthica_api.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/portfolio", tags=["Portfolio & Backtesting"], dependencies=[Depends(verify_api_key)])


def get_portfolio_service() -> PortfolioService:
    return container.portfolio_service


class PortfolioOptimizeRequest(BaseModel):
    symbols: List[str] = Field(..., min_length=2, description="List of symbols (minimum 2)")
    objective: str = Field("max_sharpe", description="'max_sharpe', 'min_volatility', or 'target_return'")
    period: str = Field("1y", description="Historical period for returns estimation: '6m', '1y', '2y', '5y'")
    risk_free_rate: float = Field(0.05, description="Annual risk-free rate (default 0.05 for 5%)")
    target_return: Optional[float] = Field(None, description="Target annual return if objective='target_return'")
    include_frontier: bool = Field(False, description="Whether to compute points on the Efficient Frontier")


class BacktestRequest(BaseModel):
    symbol: str = Field(..., description="Asset symbol to backtest")
    strategy: str = Field("sma_crossover", description="'sma_crossover', 'ema_crossover', 'rsi_reversion', 'macd_crossover', 'bollinger_reversion'")
    period: str = Field("2y", description="Historical backtest period: '1y', '2y', '5y', 'max'")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Strategy parameters e.g. {'fast_period': 20, 'slow_period': 50}")
    initial_capital: float = Field(100000.0, description="Starting cash capital")
    commission_pct: float = Field(0.001, description="Commission fee per trade (default 0.001 / 0.1%)")
    slippage_pct: float = Field(0.0005, description="Slippage per trade (default 0.0005 / 0.05%)")


@router.post("/optimize")
def optimize_portfolio_endpoint(
    req: PortfolioOptimizeRequest,
    service: PortfolioService = Depends(get_portfolio_service),
) -> Dict[str, Any]:
    """Perform Modern Portfolio Theory (MPT) optimization for maximum Sharpe or minimum variance."""
    return service.optimize(
        symbols=req.symbols,
        objective=req.objective,
        period=req.period,
        risk_free_rate=req.risk_free_rate,
        target_return=req.target_return,
        include_frontier=req.include_frontier,
    )


@router.post("/analytics")
def portfolio_analytics_endpoint(
    req: PortfolioOptimizeRequest,
    service: PortfolioService = Depends(get_portfolio_service),
) -> Dict[str, Any]:
    """Compute correlation matrix, covariance matrix, and risk metrics for a portfolio basket."""
    return service.optimize(
        symbols=req.symbols,
        objective="min_volatility",
        period=req.period,
        risk_free_rate=req.risk_free_rate,
        include_frontier=False,
    )


@router.post("/backtest")
def run_backtest_endpoint(
    req: BacktestRequest,
    service: PortfolioService = Depends(get_portfolio_service),
) -> Dict[str, Any]:
    """Execute strategy backtesting on historical data, returning trade log, Sharpe, Drawdown, and Equity Curve."""
    return service.run_backtest(
        symbol=req.symbol,
        strategy=req.strategy,
        period=req.period,
        params=req.params,
        initial_capital=req.initial_capital,
        commission_pct=req.commission_pct,
        slippage_pct=req.slippage_pct,
    )
