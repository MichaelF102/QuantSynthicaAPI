from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class ResponseMetadata(BaseModel):
    source: str = Field(description="Primary provider source, e.g. yfinance, tradingview, screener")
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cached: bool = Field(default=False, description="Whether this response was served from cache")
    latency_ms: Optional[float] = Field(default=None, description="Time taken to fetch/compute")

class MultiSourceMetadata(BaseModel):
    sources: Dict[str, str] = Field(default_factory=dict, description="Field to provider mapping")
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cached: bool = Field(default=False)
    successful_providers: List[str] = Field(default_factory=list)
    failed_providers: List[Dict[str, Any]] = Field(default_factory=list)

class ResolvedSymbol(BaseModel):
    input: str
    canonical: str
    symbol: str
    exchange: Optional[str] = None
    nse: Optional[str] = None
    bse: Optional[str] = None
    tradingview: Optional[str] = None
    screener: Optional[str] = None
    yfinance: Optional[str] = None
    country: str = "IN"
