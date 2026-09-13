"""Technical indicators engine."""

from typing import Dict, Any
import numpy as np
import pandas as pd


def calculate_sma(series: pd.Series, period: int = 20) -> pd.Series:
    return series.rolling(period).mean()


def calculate_ema(series: pd.Series, period: int = 20) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi.fillna(50.0)


def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
    fast_ema = series.ewm(span=fast, adjust=False).mean()
    slow_ema = series.ewm(span=slow, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return {"macd": macd_line, "signal": signal_line, "histogram": hist}


def calculate_bollinger_bands(series: pd.Series, period: int = 20, num_std: float = 2.0) -> Dict[str, pd.Series]:
    middle = series.rolling(period).mean()
    std = series.rolling(period).std(ddof=0)
    upper = middle + (num_std * std)
    lower = middle - (num_std * std)
    return {"upper": upper, "middle": middle, "lower": lower}


def compute_all_technicals(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute comprehensive technical snapshot from OHLCV dataframe."""
    closes = df["close"].astype(float)
    sma20 = calculate_sma(closes, 20)
    sma50 = calculate_sma(closes, 50)
    sma200 = calculate_sma(closes, 200)
    ema20 = calculate_ema(closes, 20)
    rsi14 = calculate_rsi(closes, 14)
    macd = calculate_macd(closes)
    bb = calculate_bollinger_bands(closes)

    last_idx = -1
    return {
        "last_price": round(float(closes.iloc[last_idx]), 2),
        "sma_20": round(float(sma20.iloc[last_idx]), 2) if not pd.isna(sma20.iloc[last_idx]) else None,
        "sma_50": round(float(sma50.iloc[last_idx]), 2) if not pd.isna(sma50.iloc[last_idx]) else None,
        "sma_200": round(float(sma200.iloc[last_idx]), 2) if not pd.isna(sma200.iloc[last_idx]) else None,
        "ema_20": round(float(ema20.iloc[last_idx]), 2) if not pd.isna(ema20.iloc[last_idx]) else None,
        "rsi_14": round(float(rsi14.iloc[last_idx]), 2) if not pd.isna(rsi14.iloc[last_idx]) else None,
        "macd": round(float(macd["macd"].iloc[last_idx]), 2) if not pd.isna(macd["macd"].iloc[last_idx]) else None,
        "macd_signal": round(float(macd["signal"].iloc[last_idx]), 2) if not pd.isna(macd["signal"].iloc[last_idx]) else None,
        "bollinger_upper": round(float(bb["upper"].iloc[last_idx]), 2) if not pd.isna(bb["upper"].iloc[last_idx]) else None,
        "bollinger_middle": round(float(bb["middle"].iloc[last_idx]), 2) if not pd.isna(bb["middle"].iloc[last_idx]) else None,
        "bollinger_lower": round(float(bb["lower"].iloc[last_idx]), 2) if not pd.isna(bb["lower"].iloc[last_idx]) else None,
    }
