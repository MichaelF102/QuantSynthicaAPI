from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from quant_synthica_api.schemas.common import ResponseMetadata

class QuoteData(BaseModel):
    symbol: str
    name: Optional[str] = None
    exchange: Optional[str] = None
    currency: Optional[str] = "INR"
    price: Optional[float] = Field(None, description="Normalized current or last market price")
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    previous_close: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    avg_volume: Optional[int] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    timestamp: Optional[datetime] = None

class QuoteResponse(BaseModel):
    data: QuoteData
    metadata: ResponseMetadata

class OHLCVItem(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    adj_close: Optional[float] = None
    volume: int

class HistoryResponse(BaseModel):
    symbol: str
    period: str
    interval: str
    count: int
    data: List[OHLCVItem]
    metadata: ResponseMetadata

class DividendItem(BaseModel):
    date: str
    dividend: float

class DividendsResponse(BaseModel):
    symbol: str
    count: int
    data: List[DividendItem]
    metadata: ResponseMetadata

class SplitItem(BaseModel):
    date: str
    split_ratio: float

class SplitsResponse(BaseModel):
    symbol: str
    count: int
    data: List[SplitItem]
    metadata: ResponseMetadata

# Extended yfinance Schemas
class RecommendationItem(BaseModel):
    period: Optional[str] = None
    strong_buy: Optional[int] = None
    buy: Optional[int] = None
    hold: Optional[int] = None
    sell: Optional[int] = None
    strong_sell: Optional[int] = None

class PriceTargetData(BaseModel):
    current: Optional[float] = None
    low: Optional[float] = None
    high: Optional[float] = None
    mean: Optional[float] = None
    median: Optional[float] = None

class AnalystRecommendationsResponse(BaseModel):
    symbol: str
    target_price: Optional[PriceTargetData] = None
    recommendations: List[RecommendationItem] = Field(default_factory=list)
    consensus: Optional[str] = None
    metadata: ResponseMetadata

class UpgradeDowngradeItem(BaseModel):
    date: str
    firm: Optional[str] = None
    to_grade: Optional[str] = None
    from_grade: Optional[str] = None
    action: Optional[str] = None

class UpgradesDowngradesResponse(BaseModel):
    symbol: str
    count: int
    items: List[UpgradeDowngradeItem] = Field(default_factory=list)
    metadata: ResponseMetadata

class OptionContractItem(BaseModel):
    contract_symbol: str
    strike: float
    last_price: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    change: Optional[float] = None
    percent_change: Optional[float] = None
    volume: Optional[int] = None
    open_interest: Optional[int] = None
    implied_volatility: Optional[float] = None
    in_the_money: Optional[bool] = None

class OptionsChainResponse(BaseModel):
    symbol: str
    expiration_date: str
    all_expirations: List[str] = Field(default_factory=list)
    calls: List[OptionContractItem] = Field(default_factory=list)
    puts: List[OptionContractItem] = Field(default_factory=list)
    metadata: ResponseMetadata

class NewsItem(BaseModel):
    id: Optional[str] = None
    title: str
    publisher: Optional[str] = None
    link: str
    published_at: Optional[str] = None
    type: Optional[str] = None

class NewsResponse(BaseModel):
    symbol: str
    count: int
    news: List[NewsItem]
    metadata: ResponseMetadata
