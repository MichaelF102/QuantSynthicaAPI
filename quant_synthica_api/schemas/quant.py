from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from quant_synthica_api.schemas.common import ResponseMetadata

class ReturnsMetrics(BaseModel):
    symbol: str
    daily_return: Optional[float] = Field(None, description="Most recent daily percentage return")
    cumulative_return: Optional[float] = Field(None, description="Cumulative return over period")
    cagr: Optional[float] = Field(None, description="Compound Annual Growth Rate")
    one_month_return: Optional[float] = None
    three_month_return: Optional[float] = None
    six_month_return: Optional[float] = None
    one_year_return: Optional[float] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None

class ReturnsResponse(BaseModel):
    data: ReturnsMetrics
    metadata: ResponseMetadata

class RiskMetrics(BaseModel):
    symbol: str
    annualized_volatility: Optional[float] = None
    downside_deviation: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    var_95: Optional[float] = Field(None, description="Daily Value at Risk (95% confidence)")
    cvar_95: Optional[float] = Field(None, description="Daily Conditional VaR / Expected Shortfall (95%)")
    beta: Optional[float] = None
    alpha: Optional[float] = None
    risk_free_rate: float = 0.06

class RiskResponse(BaseModel):
    data: RiskMetrics
    metadata: ResponseMetadata

class VolatilityMetrics(BaseModel):
    symbol: str
    daily_volatility: Optional[float] = None
    annualized_volatility: Optional[float] = None
    rolling_20d_volatility: Optional[float] = None
    parkinson_volatility: Optional[float] = None
    atr_14: Optional[float] = None

class VolatilityResponse(BaseModel):
    data: VolatilityMetrics
    metadata: ResponseMetadata

class TechnicalIndicators(BaseModel):
    symbol: str
    last_price: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    atr_14: Optional[float] = None
    adx_14: Optional[float] = None
    vwap: Optional[float] = None

class TechnicalResponse(BaseModel):
    data: TechnicalIndicators
    metadata: ResponseMetadata

class QuantSummaryData(BaseModel):
    symbol: str
    returns: ReturnsMetrics
    risk: RiskMetrics
    technical: TechnicalIndicators

class QuantSummaryResponse(BaseModel):
    data: QuantSummaryData
    metadata: ResponseMetadata
