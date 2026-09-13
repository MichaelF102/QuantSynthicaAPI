from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Text, JSON, Index, UniqueConstraint
)
from quant_synthica_api.database.connection import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    exchange = Column(String(50), nullable=True)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    country = Column(String(50), default="IN")
    currency = Column(String(10), default="INR")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class SymbolMappingModel(Base):
    __tablename__ = "symbols"

    id = Column(Integer, primary_key=True, index=True)
    canonical = Column(String(50), unique=True, index=True, nullable=False)
    symbol = Column(String(50), index=True, nullable=False)
    exchange = Column(String(50), nullable=True)
    nse = Column(String(50), nullable=True)
    bse = Column(String(50), nullable=True)
    tradingview = Column(String(100), nullable=True)
    screener = Column(String(50), nullable=True)
    yfinance = Column(String(50), nullable=True)

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), index=True, nullable=False)
    date = Column(String(50), index=True, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    adj_close = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("symbol", "date", name="uix_symbol_date"),
    )

class FinancialStatementModel(Base):
    __tablename__ = "financial_statements"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), index=True, nullable=False)
    statement_type = Column(String(50), index=True, nullable=False)
    period = Column(String(50), nullable=True)
    data_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class FundamentalMetricModel(Base):
    __tablename__ = "fundamentals"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), index=True, nullable=False)
    metric = Column(String(100), index=True, nullable=False)
    value = Column(Float, nullable=True)
    period = Column(String(50), nullable=True)
    source = Column(String(50), nullable=False)
    retrieved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ShareholdingModel(Base):
    __tablename__ = "shareholding"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), index=True, nullable=False)
    period = Column(String(50), index=True, nullable=False)
    category = Column(String(100), nullable=False)
    percentage = Column(Float, nullable=True)

class ScreeningResultModel(Base):
    __tablename__ = "screening_results"

    id = Column(Integer, primary_key=True, index=True)
    query_hash = Column(String(64), index=True, nullable=False)
    market = Column(String(50), nullable=False)
    total_count = Column(Integer, nullable=False)
    results_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ProviderLogModel(Base):
    __tablename__ = "provider_logs"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), index=True, nullable=False)
    endpoint = Column(String(100), index=True, nullable=False)
    symbol = Column(String(50), nullable=True)
    success = Column(Boolean, default=True)
    error = Column(Text, nullable=True)
    latency_ms = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
