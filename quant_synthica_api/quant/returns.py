from typing import List, Optional, Tuple
import pandas as pd
import numpy as np
from quant_synthica_api.schemas.market import OHLCVItem
from quant_synthica_api.schemas.quant import ReturnsMetrics

def calculate_returns(items: List[OHLCVItem], symbol: str) -> ReturnsMetrics:
    if not items or len(items) < 2:
        return ReturnsMetrics(symbol=symbol)

    df = pd.DataFrame([item.model_dump() for item in items])
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["close"])
    if len(df) < 2:
        return ReturnsMetrics(symbol=symbol)

    closes = df["close"].values
    pct_changes = np.diff(closes) / closes[:-1]
    
    daily_ret = float(pct_changes[-1]) if len(pct_changes) > 0 else 0.0
    cum_ret = float((closes[-1] - closes[0]) / closes[0]) if closes[0] != 0 else 0.0

    # Calculate CAGR
    num_days = len(df)
    # Estimate years assuming ~252 trading days/year
    years = num_days / 252.0
    if years > 0 and closes[0] > 0 and closes[-1] > 0:
        cagr = float((closes[-1] / closes[0]) ** (1.0 / years) - 1.0)
    else:
        cagr = cum_ret

    def get_period_return(days: int) -> Optional[float]:
        if len(closes) > days and closes[-days - 1] > 0:
            return round(float((closes[-1] - closes[-days - 1]) / closes[-days - 1]), 4)
        return None

    # Trading days approximations: 1M=21, 3M=63, 6M=126, 12M=252
    m1 = get_period_return(21)
    m3 = get_period_return(63)
    m6 = get_period_return(126)
    m12 = get_period_return(252)

    return ReturnsMetrics(
        symbol=symbol,
        daily_return=round(daily_ret, 4),
        cumulative_return=round(cum_ret, 4),
        cagr=round(cagr, 4),
        one_month_return=m1,
        three_month_return=m3,
        six_month_return=m6,
        one_year_return=m12,
        period_start=str(df["date"].iloc[0]),
        period_end=str(df["date"].iloc[-1]),
    )
