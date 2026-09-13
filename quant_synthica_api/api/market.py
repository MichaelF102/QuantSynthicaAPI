from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from quant_synthica_api.schemas.market import (
    QuoteResponse, HistoryResponse, DividendsResponse, SplitsResponse,
    AnalystRecommendationsResponse, UpgradesDowngradesResponse,
    OptionsChainResponse, NewsResponse
)
from quant_synthica_api.services.market_service import MarketService
from quant_synthica_api.services.container import get_market_service
from quant_synthica_api.core.security import verify_api_key

router = APIRouter(prefix="/market", tags=["Market Data"], dependencies=[Depends(verify_api_key)])

@router.get("/{symbol}/quote", response_model=QuoteResponse, summary="Get real-time / latest stock quote")
def get_stock_quote(
    symbol: str,
    market_service: MarketService = Depends(get_market_service)
):
    try:
        return market_service.get_quote(symbol)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/history", response_model=HistoryResponse, summary="Get historical OHLCV data")
def get_stock_history(
    symbol: str,
    period: str = Query(default="1y", description="Data period e.g. 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max"),
    interval: str = Query(default="1d", description="Bar interval e.g. 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo"),
    market_service: MarketService = Depends(get_market_service)
):
    try:
        return market_service.get_history(symbol, period=period, interval=interval)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/dividends", response_model=DividendsResponse, summary="Get dividend history")
def get_stock_dividends(
    symbol: str,
    market_service: MarketService = Depends(get_market_service)
):
    try:
        return market_service.get_dividends(symbol)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/splits", response_model=SplitsResponse, summary="Get stock split history")
def get_stock_splits(
    symbol: str,
    market_service: MarketService = Depends(get_market_service)
):
    try:
        return market_service.get_splits(symbol)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# --- Extended yfinance Market Endpoints ---

@router.get("/{symbol}/recommendations", response_model=AnalystRecommendationsResponse, summary="Get analyst consensus and price targets")
def get_analyst_recommendations(
    symbol: str,
    market_service: MarketService = Depends(get_market_service)
):
    try:
        return market_service.get_recommendations(symbol)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/upgrades-downgrades", response_model=UpgradesDowngradesResponse, summary="Get historical analyst rating changes")
def get_upgrades_downgrades(
    symbol: str,
    limit: int = Query(default=25, ge=1, le=100),
    market_service: MarketService = Depends(get_market_service)
):
    try:
        return market_service.get_upgrades_downgrades(symbol, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/options", response_model=OptionsChainResponse, summary="Get options chain (calls and puts) by expiration date")
def get_options_chain(
    symbol: str,
    date: Optional[str] = Query(default=None, description="Expiration date e.g. YYYY-MM-DD. If omitted, earliest expiration is returned"),
    market_service: MarketService = Depends(get_market_service)
):
    try:
        return market_service.get_options_chain(symbol, date=date)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/news", response_model=NewsResponse, summary="Get latest corporate news and press releases")
def get_company_news(
    symbol: str,
    market_service: MarketService = Depends(get_market_service)
):
    try:
        return market_service.get_news(symbol)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
