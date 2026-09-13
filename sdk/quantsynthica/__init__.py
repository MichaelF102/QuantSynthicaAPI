"""QuantSynthica Python Library.

A standalone, serverless financial intelligence and quantitative finance library
combining yfinance, TradingView-Screener, DCF valuation, Piotroski scoring,
Markowitz Modern Portfolio Theory, algorithmic backtesting, and sentiment analysis.
"""

from typing import List, Optional, Dict, Any
import pandas as pd

# Direct Ticker & Stock interface (Zero-Server, like yfinance)
from quantsynthica.ticker import Ticker, Stock

# Direct TradingView Multi-Asset Screener
from quantsynthica.screener import screener

# Direct Portfolio & Backtest Engines
from quantsynthica.engine.portfolio import optimize_portfolio as _opt_port
from quantsynthica.engine.backtest import run_backtest as _run_bt
from quantsynthica.engine.sentiment import analyze_sentiment as _analyze_sent

# Remote Client (for connecting to a hosted QuantSynthica API server)
from quantsynthica.client import QuantSynthica, Client
from quantsynthica.exceptions import (
    QuantSynthicaError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerInternalError,
    APIConnectionError,
)

__version__ = "1.1.1"


# Convenient top-level functions (no server needed)
def get_quote(symbol: str):
    """Fetch live price, day change, 52w high/low, and valuation ratios."""
    return Ticker(symbol).quote()


def get_history(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Fetch historical OHLCV price bars as a pandas DataFrame."""
    return Ticker(symbol).history(period=period, interval=interval)


def get_valuation(symbol: str):
    """Compute 4-in-1 valuation suite (DCF, Piotroski F-Score, Altman Z-Score, Graham Number)."""
    return Ticker(symbol).valuation()


def get_financials(symbol: str, quarterly: bool = False) -> pd.DataFrame:
    """Fetch income statement (annual or quarterly) as a pandas DataFrame."""
    return Ticker(symbol).financials(quarterly=quarterly)


def get_balance_sheet(symbol: str, quarterly: bool = False) -> pd.DataFrame:
    """Fetch balance sheet statement (annual or quarterly) as a pandas DataFrame."""
    return Ticker(symbol).balance_sheet(quarterly=quarterly)


def get_cashflow(symbol: str, quarterly: bool = False) -> pd.DataFrame:
    """Fetch cash flow statement (annual or quarterly) as a pandas DataFrame."""
    return Ticker(symbol).cashflow(quarterly=quarterly)


def get_ratios(symbol: str):
    """Fetch key valuation, profitability, liquidity, and solvency ratios."""
    return Ticker(symbol).ratios()


def get_analyst_targets(symbol: str):
    """Fetch consensus analyst price targets and recommendations."""
    return Ticker(symbol).analyst_targets()


def get_profile(symbol: str):
    """Fetch company description, sector, industry, and corporate profile."""
    return Ticker(symbol).profile()


def get_technicals(symbol: str, period: str = "1y"):
    """Compute SMA, EMA, RSI, MACD, and Bollinger Bands."""
    return Ticker(symbol).technicals(period=period)


def get_sentiment(symbol_or_text: str):
    """Analyze news sentiment for a ticker symbol, or score arbitrary financial commentary."""
    if len(symbol_or_text.split()) > 2:
        return _analyze_sent(symbol_or_text)
    return Ticker(symbol_or_text).sentiment()


def optimize_portfolio(
    symbols: List[str],
    objective: str = "max_sharpe",
    period: str = "1y",
    risk_free_rate: float = 0.05,
):
    """Optimize multi-asset portfolio weights for Max Sharpe or Min Volatility."""
    all_series = {}
    for s in symbols:
        df = Ticker(s).history(period=period)
        if not df.empty and "close" in df.columns:
            all_series[s] = df["close"].pct_change().dropna()
    returns_df = pd.DataFrame(all_series).dropna()
    return _opt_port(returns_df, risk_free_rate=risk_free_rate, objective=objective)


def backtest(
    symbol: str,
    strategy: str = "sma_crossover",
    period: str = "2y",
    params: Optional[Dict[str, Any]] = None,
    initial_capital: float = 100000.0,
):
    """Backtest an algorithmic trading strategy (SMA Crossover, RSI Reversion)."""
    df = Ticker(symbol).history(period=period)
    return _run_bt(df, strategy=strategy, params=params, initial_capital=initial_capital)


__all__ = [
    "Ticker",
    "Stock",
    "screener",
    "get_quote",
    "get_history",
    "get_valuation",
    "get_financials",
    "get_balance_sheet",
    "get_cashflow",
    "get_ratios",
    "get_analyst_targets",
    "get_profile",
    "get_technicals",
    "get_sentiment",
    "optimize_portfolio",
    "backtest",
    "QuantSynthica",
    "Client",
    "QuantSynthicaError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerInternalError",
    "APIConnectionError",
]
