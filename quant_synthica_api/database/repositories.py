from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from quant_synthica_api.database.models import (
    Company, SymbolMappingModel, PriceHistory, FinancialStatementModel,
    FundamentalMetricModel, ShareholdingModel, ScreeningResultModel, ProviderLogModel
)
from quant_synthica_api.schemas.market import OHLCVItem
from quant_synthica_api.schemas.common import ResolvedSymbol
from quant_synthica_api.core.logging import logger

class DatabaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_provider_call(
        self, provider: str, endpoint: str, symbol: Optional[str],
        success: bool, error: Optional[str] = None, latency_ms: Optional[float] = None
    ):
        try:
            log_entry = ProviderLogModel(
                provider=provider,
                endpoint=endpoint,
                symbol=symbol,
                success=success,
                error=error,
                latency_ms=latency_ms,
                timestamp=datetime.now(timezone.utc)
            )
            self.db.add(log_entry)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.debug(f"Failed to log provider call: {e}")

    def save_price_history(self, symbol: str, items: List[OHLCVItem]):
        try:
            for item in items:
                existing = self.db.query(PriceHistory).filter_by(symbol=symbol, date=item.date).first()
                if not existing:
                    rec = PriceHistory(
                        symbol=symbol,
                        date=item.date,
                        open=item.open,
                        high=item.high,
                        low=item.low,
                        close=item.close,
                        adj_close=item.adj_close,
                        volume=item.volume
                    )
                    self.db.add(rec)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.debug(f"Failed to save price history: {e}")

    def save_symbol_mapping(self, sym: ResolvedSymbol):
        try:
            existing = self.db.query(SymbolMappingModel).filter_by(canonical=sym.canonical).first()
            if not existing:
                rec = SymbolMappingModel(
                    canonical=sym.canonical,
                    symbol=sym.symbol,
                    exchange=sym.exchange,
                    nse=sym.nse,
                    bse=sym.bse,
                    tradingview=sym.tradingview,
                    screener=sym.screener,
                    yfinance=sym.yfinance
                )
                self.db.add(rec)
                self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.debug(f"Failed to save symbol mapping: {e}")
