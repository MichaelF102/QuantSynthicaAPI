from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from quant_synthica_api.schemas.common import ResponseMetadata, MultiSourceMetadata

class FinancialRow(BaseModel):
    metric: str
    values: Dict[str, Optional[float]] = Field(default_factory=dict)

class FinancialStatementData(BaseModel):
    statement_type: str
    periods: List[str] = Field(default_factory=list)
    rows: List[FinancialRow] = Field(default_factory=list)
    raw_data: Optional[Dict[str, Any]] = None

class FinancialStatementResponse(BaseModel):
    symbol: str
    statement_type: str
    data: FinancialStatementData
    metadata: ResponseMetadata

class RatiosData(BaseModel):
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    roce: Optional[float] = None
    debt_to_equity: Optional[float] = None
    dividend_yield: Optional[float] = None
    book_value: Optional[float] = None
    market_cap: Optional[float] = None
    current_price: Optional[float] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    face_value: Optional[float] = None
    historical_ratios: Optional[Dict[str, Dict[str, Optional[float]]]] = None

class RatiosResponse(BaseModel):
    symbol: str
    data: RatiosData
    metadata: ResponseMetadata

class ShareholdingItem(BaseModel):
    holder_category: str
    values: Dict[str, Optional[float]] = Field(default_factory=dict)

class ShareholdingResponse(BaseModel):
    symbol: str
    periods: List[str] = Field(default_factory=list)
    categories: List[ShareholdingItem] = Field(default_factory=list)
    metadata: ResponseMetadata

class UnifiedFundamentalsData(BaseModel):
    symbol: str
    name: Optional[str] = None
    about: Optional[str] = None
    ratios: RatiosData
    quarterly_results: Optional[FinancialStatementData] = None
    profit_and_loss: Optional[FinancialStatementData] = None
    balance_sheet: Optional[FinancialStatementData] = None
    cash_flow: Optional[FinancialStatementData] = None
    shareholding: Optional[List[ShareholdingItem]] = None

class UnifiedFundamentalsResponse(BaseModel):
    symbol: str
    data: UnifiedFundamentalsData
    metadata: MultiSourceMetadata

# Extended Intelligence Schemas
class HolderItem(BaseModel):
    holder: str
    shares: Optional[int] = None
    date_reported: Optional[str] = None
    percent_out: Optional[float] = None
    value: Optional[float] = None

class HoldersResponse(BaseModel):
    symbol: str
    type: str # institutional or mutualfund
    holders: List[HolderItem] = Field(default_factory=list)
    metadata: ResponseMetadata

class InsiderTransactionItem(BaseModel):
    insider_name: str
    relation: Optional[str] = None
    transaction_date: Optional[str] = None
    transaction_type: Optional[str] = None
    shares: Optional[int] = None
    value: Optional[float] = None

class InsiderTransactionsResponse(BaseModel):
    symbol: str
    count: int
    transactions: List[InsiderTransactionItem] = Field(default_factory=list)
    metadata: ResponseMetadata

class ESGRatingsData(BaseModel):
    total_esg: Optional[float] = None
    environment_score: Optional[float] = None
    social_score: Optional[float] = None
    governance_score: Optional[float] = None
    percentile: Optional[float] = None
    esg_performance: Optional[str] = None
    peer_group: Optional[str] = None

class SustainabilityResponse(BaseModel):
    symbol: str
    data: Optional[ESGRatingsData] = None
    metadata: ResponseMetadata

class PeerItem(BaseModel):
    name: str
    price: Optional[float] = None
    pe: Optional[float] = None
    market_cap: Optional[float] = None
    dividend_yield: Optional[float] = None
    net_profit_quarter: Optional[float] = None
    qtr_profit_var: Optional[float] = None
    sales_quarter: Optional[float] = None
    qtr_sales_var: Optional[float] = None
    roce: Optional[float] = None

class PeersResponse(BaseModel):
    symbol: str
    sector: Optional[str] = None
    peers: List[PeerItem] = Field(default_factory=list)
    metadata: ResponseMetadata

class CorporateAnalysisResponse(BaseModel):
    symbol: str
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    metadata: ResponseMetadata

class DocumentItem(BaseModel):
    title: str
    type: str # concall, transcript, annual_report, presentation
    date: Optional[str] = None
    url: str

class DocumentsResponse(BaseModel):
    symbol: str
    count: int
    documents: List[DocumentItem] = Field(default_factory=list)
    metadata: ResponseMetadata
