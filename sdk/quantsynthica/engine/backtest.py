"""Algorithmic strategy backtesting engine."""

from typing import Dict, Any, List, Optional
import pandas as pd
from quantsynthica.resources.base import DotDict
from quantsynthica.engine.indicators import calculate_sma, calculate_rsi


def run_backtest(
    df: pd.DataFrame,
    strategy: str = "sma_crossover",
    params: Optional[Dict[str, Any]] = None,
    initial_capital: float = 100000.0,
    commission_pct: float = 0.001,
    slippage_pct: float = 0.0005,
) -> DotDict:
    if params is None:
        params = {}

    df = df.copy()
    df.columns = [c.lower() for c in df.columns]
    closes = df["close"].astype(float)
    signals = pd.Series(0, index=df.index)

    if strategy == "sma_crossover":
        fast = int(params.get("fast_period", 20))
        slow = int(params.get("slow_period", 50))
        sma_fast = calculate_sma(closes, fast)
        sma_slow = calculate_sma(closes, slow)
        signals[sma_fast > sma_slow] = 1
        signals[sma_fast <= sma_slow] = 0
    elif strategy == "rsi_reversion":
        period = int(params.get("period", 14))
        oversold = float(params.get("oversold", 30))
        overbought = float(params.get("overbought", 70))
        rsi = calculate_rsi(closes, period)
        pos = 0
        sig_list = []
        for v in rsi:
            if v < oversold:
                pos = 1
            elif v > overbought:
                pos = 0
            sig_list.append(pos)
        signals = pd.Series(sig_list, index=df.index)

    capital = initial_capital
    position = 0
    shares = 0.0
    entry_price = 0.0
    trades = []

    for i in range(len(df)):
        price = float(closes.iloc[i])
        sig = int(signals.iloc[i])

        if sig == 1 and position == 0:
            eff_price = price * (1.0 + slippage_pct)
            fee = capital * commission_pct
            avail = capital - fee
            shares = avail / eff_price
            entry_price = eff_price
            position = 1
            capital = 0.0
        elif sig == 0 and position == 1:
            eff_price = price * (1.0 - slippage_pct)
            proceeds = shares * eff_price
            fee = proceeds * commission_pct
            capital = proceeds - fee
            pnl = capital - (shares * entry_price)
            trades.append({
                "entry_price": round(entry_price, 2),
                "exit_price": round(eff_price, 2),
                "pnl": round(pnl, 2),
                "win": pnl > 0,
            })
            shares = 0.0
            position = 0

    if position == 1:
        last_price = float(closes.iloc[-1])
        eff_price = last_price * (1.0 - slippage_pct)
        proceeds = shares * eff_price
        fee = proceeds * commission_pct
        capital = proceeds - fee

    final_equity = capital
    total_return_pct = round(((final_equity - initial_capital) / initial_capital) * 100, 2)
    winning = [t for t in trades if t["win"]]
    win_rate = round((len(winning) / len(trades) * 100), 2) if trades else 0.0

    return DotDict({
        "strategy": strategy,
        "summary": {
            "initial_capital": round(initial_capital, 2),
            "final_equity": round(final_equity, 2),
            "total_return_pct": total_return_pct,
            "total_trades": len(trades),
            "win_rate_pct": win_rate,
        },
        "trades": trades,
    })
