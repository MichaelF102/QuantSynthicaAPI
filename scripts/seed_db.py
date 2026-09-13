import sys
from pathlib import Path
root = str(Path(__file__).resolve().parent.parent)
if root not in sys.path:
    sys.path.insert(0, root)

from quant_synthica_api.database.connection import SessionLocal

from quant_synthica_api.database.models import Company, SymbolMappingModel
from quant_synthica_api.services.symbol_resolver import KNOWN_MAPPINGS, SymbolResolver
from quant_synthica_api.core.logging import logger

def seed():
    db = SessionLocal()
    try:
        logger.info("Seeding known symbols and companies...")
        for sym, details in KNOWN_MAPPINGS.items():
            r = SymbolResolver.resolve(sym)
            existing_sym = db.query(SymbolMappingModel).filter_by(canonical=r.canonical).first()
            if not existing_sym:
                db.add(SymbolMappingModel(
                    canonical=r.canonical,
                    symbol=r.symbol,
                    exchange=r.exchange,
                    nse=r.nse,
                    bse=r.bse,
                    tradingview=r.tradingview,
                    screener=r.screener,
                    yfinance=r.yfinance
                ))

            existing_comp = db.query(Company).filter_by(symbol=r.symbol).first()
            if not existing_comp:
                db.add(Company(
                    symbol=r.symbol,
                    name=details.get("name", sym),
                    exchange=r.exchange,
                    country=r.country,
                    currency="INR"
                ))
        db.commit()
        logger.info("Seeding complete.")
    except Exception as e:
        db.rollback()
        logger.error(f"Seeding failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
