from quant_synthica_api.database.connection import engine, Base
from quant_synthica_api.database.models import (
    Company, SymbolMappingModel, PriceHistory, FinancialStatementModel,
    FundamentalMetricModel, ShareholdingModel, ScreeningResultModel, ProviderLogModel
)
from quant_synthica_api.core.logging import logger

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database tables: {e}")

if __name__ == "__main__":
    init_db()
