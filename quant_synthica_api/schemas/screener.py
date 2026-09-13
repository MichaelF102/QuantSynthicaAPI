from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from quant_synthica_api.schemas.common import ResponseMetadata

class ScreenerFilter(BaseModel):
    market_cap_min: Optional[float] = None
    market_cap_max: Optional[float] = None
    pe_min: Optional[float] = None
    pe_max: Optional[float] = None
    pb_max: Optional[float] = None
    roe_min: Optional[float] = None
    roce_min: Optional[float] = None
    dividend_yield_min: Optional[float] = None
    volume_min: Optional[float] = None
    rsi_min: Optional[float] = None
    rsi_max: Optional[float] = None
    sector: Optional[str] = None

class ScreenerQueryRequest(BaseModel):
    market: str = Field(default="india", description="Market/country, e.g. india, america, etc.")
    exchange: Optional[str] = Field(default="NSE", description="Exchange filter e.g. NSE, BSE, NASDAQ")
    filters: Optional[ScreenerFilter] = Field(default_factory=ScreenerFilter)
    select_columns: Optional[List[str]] = Field(default=None, description="Custom 3000+ TradingView column list (e.g. close|1, MACD.macd)")
    sort_by: Optional[str] = Field(default="market_cap_basic", description="Field to sort by")
    sort_order: Optional[str] = Field(default="desc", description="'asc' or 'desc'")
    limit: int = Field(default=20, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

class GenericScreenerRequest(BaseModel):
    sort_by: Optional[str] = None
    sort_order: Optional[str] = Field(default="desc")
    limit: int = Field(default=20, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
    select_columns: Optional[List[str]] = None

class ScreenerStockItem(BaseModel):
    ticker: str
    symbol: str
    name: Optional[str] = None
    exchange: Optional[str] = None
    price: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[float] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    sector: Optional[str] = None
    rating: Optional[str] = None
    extra_fields: Optional[Dict[str, Any]] = None

class ScreenerResponse(BaseModel):
    total_count: int
    count: int
    items: List[ScreenerStockItem]
    metadata: ResponseMetadata

class MultiAssetItem(BaseModel):
    ticker: str
    name: Optional[str] = None
    price: Optional[float] = None
    change: Optional[float] = None
    volume: Optional[float] = None
    extra_fields: Dict[str, Any] = Field(default_factory=dict)

class MultiAssetScreenerResponse(BaseModel):
    asset_class: str
    total_count: int
    count: int
    items: List[MultiAssetItem]
    metadata: ResponseMetadata
