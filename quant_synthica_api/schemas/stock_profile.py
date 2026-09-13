from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class StockIdentity(BaseModel):
    symbol: str
    name: Optional[str] = None
    exchange: Optional[str] = None
    currency: Optional[str] = "INR"
    country: Optional[str] = "IN"

class StockMarketMetrics(BaseModel):
    price: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[float] = None
    market_cap: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None

class StockValuationMetrics(BaseModel):
    pe: Optional[float] = None
    pb: Optional[float] = None
    dividend_yield: Optional[float] = None
    book_value: Optional[float] = None
    debt_to_equity: Optional[float] = None

class StockProfitabilityMetrics(BaseModel):
    roe: Optional[float] = None
    roce: Optional[float] = None
    opm: Optional[float] = None
    npm: Optional[float] = None

class StockGrowthMetrics(BaseModel):
    revenue_growth: Optional[float] = None
    profit_growth: Optional[float] = None

class StockTechnicalMetrics(BaseModel):
    rsi: Optional[float] = None
    macd: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None

class StockQuantMetrics(BaseModel):
    volatility: Optional[float] = None
    sharpe: Optional[float] = None
    max_drawdown: Optional[float] = None

class StockProfileResponse(BaseModel):
    identity: StockIdentity
    market: StockMarketMetrics
    valuation: StockValuationMetrics
    profitability: StockProfitabilityMetrics
    growth: StockGrowthMetrics
    technical: StockTechnicalMetrics
    quant: StockQuantMetrics
    sources: Dict[str, str] = Field(default_factory=dict, description="Field or section source provenance")
