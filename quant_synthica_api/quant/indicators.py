from typing import List, Optional
import numpy as np
import pandas as pd
from quant_synthica_api.schemas.market import OHLCVItem
from quant_synthica_api.schemas.quant import TechnicalIndicators

def calculate_technical_indicators(items: List[OHLCVItem], symbol: str) -> TechnicalIndicators:
    if not items or len(items) < 5:
        return TechnicalIndicators(symbol=symbol)

    df = pd.DataFrame([item.model_dump() for item in items])
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["close"])
    if len(df) < 5:
        return TechnicalIndicators(symbol=symbol)

    closes = df["close"]
    highs = df["high"]
    lows = df["low"]
    volumes = df["volume"]
    last_price = float(closes.iloc[-1])

    # SMAs
    sma_20 = float(closes.rolling(20).mean().iloc[-1]) if len(closes) >= 20 else None
    sma_50 = float(closes.rolling(50).mean().iloc[-1]) if len(closes) >= 50 else None
    sma_200 = float(closes.rolling(200).mean().iloc[-1]) if len(closes) >= 200 else None

    # EMAs
    ema_12 = float(closes.ewm(span=12, adjust=False).mean().iloc[-1]) if len(closes) >= 12 else None
    ema_26 = float(closes.ewm(span=26, adjust=False).mean().iloc[-1]) if len(closes) >= 26 else None

    # RSI (14)
    rsi_14 = None
    if len(closes) >= 15:
        delta = closes.diff().dropna()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        
        if len(gain) >= 14:
            avg_gain = float(gain.iloc[:14].mean())
            avg_loss = float(loss.iloc[:14].mean())

            for i in range(14, len(gain)):
                avg_gain = (avg_gain * 13.0 + float(gain.iloc[i])) / 14.0
                avg_loss = (avg_loss * 13.0 + float(loss.iloc[i])) / 14.0

            if avg_loss == 0:
                rsi_14 = 100.0 if avg_gain > 0 else 50.0
            else:
                rs = avg_gain / avg_loss
                rsi_14 = float(100.0 - (100.0 / (1.0 + rs)))


    # MACD (12, 26, 9)
    macd = None
    macd_signal = None
    macd_hist = None
    if len(closes) >= 35:
        fast_ema = closes.ewm(span=12, adjust=False).mean()
        slow_ema = closes.ewm(span=26, adjust=False).mean()
        macd_series = fast_ema - slow_ema
        signal_series = macd_series.ewm(span=9, adjust=False).mean()
        hist_series = macd_series - signal_series
        macd = float(macd_series.iloc[-1])
        macd_signal = float(signal_series.iloc[-1])
        macd_hist = float(hist_series.iloc[-1])

    # Bollinger Bands (20, 2)
    bb_upper = None
    bb_middle = None
    bb_lower = None
    if len(closes) >= 20:
        roll_mean = closes.rolling(20).mean()
        roll_std = closes.rolling(20).std(ddof=0)
        bb_middle = float(roll_mean.iloc[-1])
        bb_upper = float(bb_middle + 2.0 * roll_std.iloc[-1])
        bb_lower = float(bb_middle - 2.0 * roll_std.iloc[-1])

    # ATR (14)
    atr_14 = None
    if len(df) >= 15:
        tr1 = highs - lows
        tr2 = (highs - closes.shift(1)).abs()
        tr3 = (lows - closes.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr_series = tr.rolling(14).mean()
        atr_14 = float(atr_series.iloc[-1])

    # ADX (14)
    adx_14 = None
    if len(df) >= 28 and atr_14 is not None:
        try:
            up_move = highs.diff()
            down_move = -lows.diff()
            plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
            minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
            
            tr = pd.concat([highs - lows, (highs - closes.shift(1)).abs(), (lows - closes.shift(1)).abs()], axis=1).max(axis=1)
            atr_s = tr.rolling(14).mean()
            plus_di = 100.0 * (pd.Series(plus_dm).rolling(14).mean() / atr_s)
            minus_di = 100.0 * (pd.Series(minus_dm).rolling(14).mean() / atr_s)
            
            dx = 100.0 * (abs(plus_di - minus_di) / (plus_di + minus_di)).fillna(0)
            adx_series = dx.rolling(14).mean()
            adx_14 = float(adx_series.iloc[-1])
        except Exception:
            pass

    # VWAP
    vwap = None
    if volumes.sum() > 0:
        typical_price = (highs + lows + closes) / 3.0
        vwap = float((typical_price * volumes).sum() / volumes.sum())

    return TechnicalIndicators(
        symbol=symbol,
        last_price=round(last_price, 4),
        sma_20=round(sma_20, 4) if sma_20 is not None else None,
        sma_50=round(sma_50, 4) if sma_50 is not None else None,
        sma_200=round(sma_200, 4) if sma_200 is not None else None,
        ema_12=round(ema_12, 4) if ema_12 is not None else None,
        ema_26=round(ema_26, 4) if ema_26 is not None else None,
        rsi_14=round(rsi_14, 2) if rsi_14 is not None else None,
        macd=round(macd, 4) if macd is not None else None,
        macd_signal=round(macd_signal, 4) if macd_signal is not None else None,
        macd_histogram=round(macd_hist, 4) if macd_hist is not None else None,
        bollinger_upper=round(bb_upper, 4) if bb_upper is not None else None,
        bollinger_middle=round(bb_middle, 4) if bb_middle is not None else None,
        bollinger_lower=round(bb_lower, 4) if bb_lower is not None else None,
        atr_14=round(atr_14, 4) if atr_14 is not None else None,
        adx_14=round(adx_14, 2) if adx_14 is not None else None,
        vwap=round(vwap, 4) if vwap is not None else None
    )


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


def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    fast_ema = series.ewm(span=fast, adjust=False).mean()
    slow_ema = series.ewm(span=slow, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return {
        "macd": macd_line,
        "signal": signal_line,
        "histogram": hist,
    }


def calculate_bollinger_bands(series: pd.Series, period: int = 20, num_std: float = 2.0) -> dict:
    middle = series.rolling(period).mean()
    std = series.rolling(period).std(ddof=0)
    upper = middle + (num_std * std)
    lower = middle - (num_std * std)
    return {
        "upper": upper,
        "middle": middle,
        "lower": lower,
    }

