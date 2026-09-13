"""Algorithmic strategy backtesting engine.

Implements event-driven simulation for technical trading strategies:
- SMA / EMA Crossover
- RSI Mean Reversion
- MACD Signal Crossover
- Bollinger Bands Breakout / Reversion
- Trade execution simulation with slippage, commission, and metrics
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from quant_synthica_api.quant.indicators import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
)


def run_strategy_backtest(
    df: pd.DataFrame,
    strategy: str = "sma_crossover",
    params: Optional[Dict[str, Any]] = None,
    initial_capital: float = 100000.0,
    commission_pct: float = 0.001,  # 0.1% per trade
    slippage_pct: float = 0.0005,   # 0.05% slippage
) -> Dict[str, Any]:
    """Simulate strategy execution on historical OHLCV data.

    df must contain columns: ['timestamp' or 'date', 'open', 'high', 'low', 'close', 'volume'].
    """
    if params is None:
        params = {}

    df = df.copy()
    # Normalize column names
    df.columns = [c.lower() for c in df.columns]
    date_col = "date" if "date" in df.columns else ("timestamp" if "timestamp" in df.columns else df.columns[0])
    df["date_str"] = df[date_col].astype(str)

    closes = df["close"].astype(float)
    signals = pd.Series(0, index=df.index)

    # 1. Generate Strategy Signals (1: Long, -1: Flat/Exit)
    if strategy == "sma_crossover":
        fast = int(params.get("fast_period", 20))
        slow = int(params.get("slow_period", 50))
        sma_fast = calculate_sma(closes, fast)
        sma_slow = calculate_sma(closes, slow)
        signals[sma_fast > sma_slow] = 1
        signals[sma_fast <= sma_slow] = 0

    elif strategy == "ema_crossover":
        fast = int(params.get("fast_period", 12))
        slow = int(params.get("slow_period", 26))
        ema_fast = calculate_ema(closes, fast)
        ema_slow = calculate_ema(closes, slow)
        signals[ema_fast > ema_slow] = 1
        signals[ema_fast <= ema_slow] = 0

    elif strategy == "rsi_reversion":
        period = int(params.get("period", 14))
        oversold = float(params.get("oversold", 30))
        overbought = float(params.get("overbought", 70))
        rsi = calculate_rsi(closes, period)
        
        pos = 0
        sig_list = []
        for val in rsi:
            if pd.isna(val):
                sig_list.append(0)
            elif val < oversold:
                pos = 1
                sig_list.append(pos)
            elif val > overbought:
                pos = 0
                sig_list.append(pos)
            else:
                sig_list.append(pos)
        signals = pd.Series(sig_list, index=df.index)

    elif strategy == "macd_crossover":
        macd_res = calculate_macd(closes)
        macd_line = macd_res["macd"]
        signal_line = macd_res["signal"]
        signals[macd_line > signal_line] = 1
        signals[macd_line <= signal_line] = 0

    elif strategy == "bollinger_reversion":
        bb = calculate_bollinger_bands(closes)
        lower = bb["lower"]
        upper = bb["upper"]
        pos = 0
        sig_list = []
        for c, l, u in zip(closes, lower, upper):
            if pd.isna(l) or pd.isna(u):
                sig_list.append(0)
            elif c <= l:
                pos = 1
                sig_list.append(pos)
            elif c >= u:
                pos = 0
                sig_list.append(pos)
            else:
                sig_list.append(pos)
        signals = pd.Series(sig_list, index=df.index)
    else:
        raise ValueError(f"Unknown strategy: {strategy}. Supported: sma_crossover, ema_crossover, rsi_reversion, macd_crossover, bollinger_reversion")

    # 2. Simulate Portfolio and Trades
    capital = initial_capital
    position = 0  # 0: cash, 1: invested
    shares = 0.0
    entry_price = 0.0
    entry_date = ""

    trades: List[Dict[str, Any]] = []
    equity_curve: List[Dict[str, Any]] = []
    daily_returns: List[float] = []

    benchmark_initial_price = float(closes.iloc[0])
    prev_portfolio_val = initial_capital

    for i in range(len(df)):
        price = float(closes.iloc[i])
        sig = int(signals.iloc[i])
        curr_date = str(df["date_str"].iloc[i])

        # State transition: Buy
        if sig == 1 and position == 0:
            eff_price = price * (1.0 + slippage_pct)
            fee = capital * commission_pct
            avail = capital - fee
            shares = avail / eff_price
            entry_price = eff_price
            entry_date = curr_date
            position = 1
            capital = 0.0

        # State transition: Sell
        elif sig == 0 and position == 1:
            eff_price = price * (1.0 - slippage_pct)
            proceeds = shares * eff_price
            fee = proceeds * commission_pct
            capital = proceeds - fee
            pnl = capital - (shares * entry_price)
            pnl_pct = ((eff_price - entry_price) / entry_price) * 100

            trades.append({
                "entry_date": entry_date,
                "exit_date": curr_date,
                "entry_price": round(entry_price, 2),
                "exit_price": round(eff_price, 2),
                "shares": round(shares, 4),
                "pnl": round(pnl, 2),
                "return_pct": round(pnl_pct, 2),
                "win": pnl > 0,
            })
            shares = 0.0
            position = 0

        # Current portfolio equity
        if position == 1:
            curr_equity = shares * price
        else:
            curr_equity = capital

        # Benchmark equity
        bench_equity = initial_capital * (price / benchmark_initial_price)

        daily_ret = (curr_equity - prev_portfolio_val) / prev_portfolio_val if prev_portfolio_val > 0 else 0.0
        daily_returns.append(daily_ret)
        prev_portfolio_val = curr_equity

        equity_curve.append({
            "date": curr_date,
            "portfolio_value": round(curr_equity, 2),
            "benchmark_value": round(bench_equity, 2),
            "in_position": bool(position),
        })

    # Close open trade at end if still in position
    if position == 1:
        last_price = float(closes.iloc[-1])
        eff_price = last_price * (1.0 - slippage_pct)
        proceeds = shares * eff_price
        fee = proceeds * commission_pct
        capital = proceeds - fee
        pnl = capital - (shares * entry_price)
        pnl_pct = ((eff_price - entry_price) / entry_price) * 100
        trades.append({
            "entry_date": entry_date,
            "exit_date": str(df["date_str"].iloc[-1]),
            "entry_price": round(entry_price, 2),
            "exit_price": round(eff_price, 2),
            "shares": round(shares, 4),
            "pnl": round(pnl, 2),
            "return_pct": round(pnl_pct, 2),
            "win": pnl > 0,
            "closed_at_end": True,
        })
        curr_equity = capital

    # 3. Calculate Performance Metrics
    final_equity = curr_equity
    total_return_pct = ((final_equity - initial_capital) / initial_capital) * 100
    bench_final = float(equity_curve[-1]["benchmark_value"]) if equity_curve else initial_capital
    bench_return_pct = ((bench_final - initial_capital) / initial_capital) * 100

    n_days = max(1, len(df))
    years = max(n_days / 252.0, 0.01)
    cagr = (((final_equity / initial_capital) ** (1.0 / years)) - 1.0) * 100 if final_equity > 0 else -100.0

    eq_series = pd.Series([e["portfolio_value"] for e in equity_curve])
    peak = eq_series.cummax()
    drawdowns = (eq_series - peak) / peak
    max_drawdown_pct = abs(float(drawdowns.min())) * 100 if len(drawdowns) > 0 else 0.0

    ret_series = pd.Series(daily_returns)
    vol = float(ret_series.std() * np.sqrt(252))
    sharpe = float((ret_series.mean() * 252 - 0.05) / vol) if vol > 0 else 0.0

    neg_rets = ret_series[ret_series < 0]
    downside_dev = float(neg_rets.std() * np.sqrt(252)) if len(neg_rets) > 1 else vol
    sortino = float((ret_series.mean() * 252 - 0.05) / downside_dev) if downside_dev > 0 else 0.0

    # Trade statistics
    num_trades = len(trades)
    winning_trades = [t for t in trades if t["win"]]
    losing_trades = [t for t in trades if not t["win"]]
    win_rate_pct = (len(winning_trades) / num_trades * 100) if num_trades > 0 else 0.0

    gross_profit = sum(t["pnl"] for t in winning_trades)
    gross_loss = abs(sum(t["pnl"] for t in losing_trades))
    profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else (999.0 if gross_profit > 0 else 0.0)

    return {
        "strategy": strategy,
        "parameters": params,
        "summary": {
            "initial_capital": round(initial_capital, 2),
            "final_equity": round(final_equity, 2),
            "total_return_pct": round(total_return_pct, 2),
            "cagr_pct": round(cagr, 2),
            "benchmark_return_pct": round(bench_return_pct, 2),
            "alpha_vs_benchmark_pct": round(total_return_pct - bench_return_pct, 2),
            "annualized_volatility_pct": round(vol * 100, 2),
            "sharpe_ratio": round(sharpe, 2),
            "sortino_ratio": round(sortino, 2),
            "max_drawdown_pct": round(max_drawdown_pct, 2),
            "total_trades": num_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate_pct": round(win_rate_pct, 2),
            "profit_factor": profit_factor,
        },
        "trades": trades,
        "equity_curve": equity_curve[::max(1, len(equity_curve) // 100)],  # sample down to max ~100 points for light payload
    }
