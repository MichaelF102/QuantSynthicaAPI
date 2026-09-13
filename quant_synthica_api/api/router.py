from fastapi import APIRouter
from quant_synthica_api.api.market import router as market_router
from quant_synthica_api.api.fundamentals import router as fundamentals_router
from quant_synthica_api.api.screener import router as screener_router
from quant_synthica_api.api.technical import router as technical_router
from quant_synthica_api.api.quant import router as quant_router
from quant_synthica_api.api.stocks import router as stocks_router
from quant_synthica_api.api.search import router as search_router
from quant_synthica_api.api.health import router as health_router
from quant_synthica_api.api.valuation import router as valuation_router
from quant_synthica_api.api.portfolio import router as portfolio_router
from quant_synthica_api.api.sentiment import router as sentiment_router
from quant_synthica_api.api.reports import router as reports_router
from quant_synthica_api.api.websockets import ws_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health_router)
api_v1_router.include_router(search_router)
api_v1_router.include_router(market_router)
api_v1_router.include_router(fundamentals_router)
api_v1_router.include_router(screener_router)
api_v1_router.include_router(technical_router)
api_v1_router.include_router(quant_router)
api_v1_router.include_router(stocks_router)
api_v1_router.include_router(valuation_router)
api_v1_router.include_router(portfolio_router)
api_v1_router.include_router(sentiment_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(ws_router)

