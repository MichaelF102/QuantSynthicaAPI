from typing import List, Optional
import numpy as np
import pandas as pd
from quant_synthica_api.schemas.market import OHLCVItem
from quant_synthica_api.schemas.quant import RiskMetrics, VolatilityMetrics

def calculate_risk(
    items: List[OHLCVItem],
    symbol: str,
    risk_free_rate: float = 0.06,
    benchmark_items: Optional[List[OHLCVItem]] = None
) -> RiskMetrics:
    if not items or len(items) < 5:
        return RiskMetrics(symbol=symbol, risk_free_rate=risk_free_rate)

    df = pd.DataFrame([item.model_dump() for item in items])
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["close"])
    if len(df) < 5:
        return RiskMetrics(symbol=symbol, risk_free_rate=risk_free_rate)

    closes = df["close"].values
    daily_returns = np.diff(closes) / closes[:-1]

    if len(daily_returns) == 0:
        return RiskMetrics(symbol=symbol, risk_free_rate=risk_free_rate)

    # Annualized Volatility
    daily_vol = float(np.std(daily_returns, ddof=1)) if len(daily_returns) > 1 else 0.0
    ann_vol = daily_vol * np.sqrt(252)

    # Downside deviation
    daily_rf = risk_free_rate / 252.0
    negative_excess_returns = daily_returns[daily_returns < daily_rf] - daily_rf
    if len(negative_excess_returns) > 1:
        downside_dev = float(np.sqrt(np.mean(negative_excess_returns ** 2))) * np.sqrt(252)
    else:
        downside_dev = ann_vol

    # Annualized return
    mean_daily_return = float(np.mean(daily_returns))
    ann_return = mean_daily_return * 252.0

    # Sharpe Ratio
    sharpe = (ann_return - risk_free_rate) / ann_vol if ann_vol > 0 else 0.0

    # Sortino Ratio
    sortino = (ann_return - risk_free_rate) / downside_dev if downside_dev > 0 else 0.0

    # Maximum Drawdown
    cum_max = np.maximum.accumulate(closes)
    drawdowns = (closes - cum_max) / cum_max
    max_dd = float(np.min(drawdowns))

    # VaR 95% & CVaR 95%
    var_95 = float(np.percentile(daily_returns, 5))
    cvar_returns = daily_returns[daily_returns <= var_95]
    cvar_95 = float(np.mean(cvar_returns)) if len(cvar_returns) > 0 else var_95

    # Beta and Alpha calculation
    beta: Optional[float] = None
    alpha: Optional[float] = None
    if benchmark_items and len(benchmark_items) >= len(items):
        try:
            b_df = pd.DataFrame([b.model_dump() for b in benchmark_items])
            b_df["close"] = pd.to_numeric(b_df["close"], errors="coerce")
            b_closes = b_df["close"].values
            b_returns = np.diff(b_closes) / b_closes[:-1]
            min_len = min(len(daily_returns), len(b_returns))
            s_ret = daily_returns[-min_len:]
            b_ret = b_returns[-min_len:]
            cov = np.cov(s_ret, b_ret)[0][1]
            b_var = np.var(b_ret, ddof=1)
            if b_var > 0:
                beta = float(cov / b_var)
                alpha = float(ann_return - (risk_free_rate + beta * (np.mean(b_ret) * 252.0 - risk_free_rate)))
        except Exception:
            pass

    return RiskMetrics(
        symbol=symbol,
        annualized_volatility=round(ann_vol, 4),
        downside_deviation=round(downside_dev, 4),
        sharpe_ratio=round(sharpe, 4),
        sortino_ratio=round(sortino, 4),
        max_drawdown=round(max_dd, 4),
        var_95=round(var_95, 4),
        cvar_95=round(cvar_95, 4),
        beta=round(beta, 4) if beta is not None else None,
        alpha=round(alpha, 4) if alpha is not None else None,
        risk_free_rate=risk_free_rate
    )

def calculate_volatility_metrics(items: List[OHLCVItem], symbol: str) -> VolatilityMetrics:
    if not items or len(items) < 5:
        return VolatilityMetrics(symbol=symbol)

    df = pd.DataFrame([item.model_dump() for item in items])
    for c in ["open", "high", "low", "close"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    closes = df["close"].values
    daily_returns = np.diff(closes) / closes[:-1]
    daily_vol = float(np.std(daily_returns, ddof=1)) if len(daily_returns) > 1 else 0.0
    ann_vol = daily_vol * np.sqrt(252)

    # 20-day rolling volatility
    rolling_20 = None
    if len(daily_returns) >= 20:
        rolling_20 = float(np.std(daily_returns[-20:], ddof=1) * np.sqrt(252))

    # Parkinson Volatility using High/Low
    highs = df["high"].values
    lows = df["low"].values
    mask = (highs > 0) & (lows > 0) & (highs >= lows)
    if np.sum(mask) >= 5:
        hl_ratio = np.log(highs[mask] / lows[mask]) ** 2
        parkinson = float(np.sqrt((1.0 / (4.0 * np.log(2) * len(hl_ratio))) * np.sum(hl_ratio)) * np.sqrt(252))
    else:
        parkinson = None

    # ATR (14)
    atr = None
    if len(df) >= 15:
        tr_list = []
        for i in range(1, len(df)):
            h = highs[i]
            l = lows[i]
            prev_c = closes[i-1]
            tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
            tr_list.append(tr)
        if len(tr_list) >= 14:
            atr = float(pd.Series(tr_list).rolling(14).mean().iloc[-1])

    return VolatilityMetrics(
        symbol=symbol,
        daily_volatility=round(daily_vol, 4),
        annualized_volatility=round(ann_vol, 4),
        rolling_20d_volatility=round(rolling_20, 4) if rolling_20 else None,
        parkinson_volatility=round(parkinson, 4) if parkinson else None,
        atr_14=round(atr, 4) if atr else None
    )
