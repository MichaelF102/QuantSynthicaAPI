from fastapi import APIRouter, Depends, Query, HTTPException, status
from quant_synthica_api.schemas.screener import (
    ScreenerQueryRequest, ScreenerResponse, GenericScreenerRequest, MultiAssetScreenerResponse
)
from quant_synthica_api.services.screener_service import ScreenerService
from quant_synthica_api.services.container import get_screener_service
from quant_synthica_api.core.security import verify_api_key

router = APIRouter(prefix="/screener", tags=["Screener"], dependencies=[Depends(verify_api_key)])

@router.post("/query", response_model=ScreenerResponse, summary="Execute custom stock screener query")
def query_screener(
    req: ScreenerQueryRequest,
    screener_service: ScreenerService = Depends(get_screener_service)
):
    try:
        return screener_service.query(req)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/value", response_model=ScreenerResponse, summary="Predefined screen: Value stocks")
def get_value_screen(
    market: str = Query(default="india", description="Market country"),
    limit: int = Query(default=20, ge=1, le=100),
    screener_service: ScreenerService = Depends(get_screener_service)
):
    try:
        return screener_service.get_value_stocks(market=market, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/growth", response_model=ScreenerResponse, summary="Predefined screen: High Growth stocks")
def get_growth_screen(
    market: str = Query(default="india", description="Market country"),
    limit: int = Query(default=20, ge=1, le=100),
    screener_service: ScreenerService = Depends(get_screener_service)
):
    try:
        return screener_service.get_growth_stocks(market=market, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/momentum", response_model=ScreenerResponse, summary="Predefined screen: Momentum stocks")
def get_momentum_screen(
    market: str = Query(default="india", description="Market country"),
    limit: int = Query(default=20, ge=1, le=100),
    screener_service: ScreenerService = Depends(get_screener_service)
):
    try:
        return screener_service.get_momentum_stocks(market=market, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/dividend", response_model=ScreenerResponse, summary="Predefined screen: High Dividend Yield stocks")
def get_dividend_screen(
    market: str = Query(default="india", description="Market country"),
    limit: int = Query(default=20, ge=1, le=100),
    screener_service: ScreenerService = Depends(get_screener_service)
):
    try:
        return screener_service.get_dividend_stocks(market=market, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# --- TradingView Multi-Asset Screeners ---

@router.post("/crypto", response_model=MultiAssetScreenerResponse, summary="TradingView Crypto Pairs Screener")
def query_crypto_screener(
    req: GenericScreenerRequest = GenericScreenerRequest(),
    screener_service: ScreenerService = Depends(get_screener_service)
):
    try:
        return screener_service.query_multi_asset("crypto", req)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/coin", response_model=MultiAssetScreenerResponse, summary="TradingView CoinMarketCap Coins Screener")
def query_coin_screener(
    req: GenericScreenerRequest = GenericScreenerRequest(),
    screener_service: ScreenerService = Depends(get_screener_service)
):
    try:
        return screener_service.query_multi_asset("coin", req)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/forex", response_model=MultiAssetScreenerResponse, summary="TradingView Forex Screener")
def query_forex_screener(
    req: GenericScreenerRequest = GenericScreenerRequest(),
    screener_service: ScreenerService = Depends(get_screener_service)
):
    try:
        return screener_service.query_multi_asset("forex", req)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/futures", response_model=MultiAssetScreenerResponse, summary="TradingView Commodity & Index Futures Screener")
def query_futures_screener(
    req: GenericScreenerRequest = GenericScreenerRequest(),
    screener_service: ScreenerService = Depends(get_screener_service)
):
    try:
        return screener_service.query_multi_asset("futures", req)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/bonds", response_model=MultiAssetScreenerResponse, summary="TradingView Sovereign & Corporate Bonds Screener")
def query_bonds_screener(
    req: GenericScreenerRequest = GenericScreenerRequest(),
    screener_service: ScreenerService = Depends(get_screener_service)
):
    try:
        return screener_service.query_multi_asset("bonds", req)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/cfd", response_model=MultiAssetScreenerResponse, summary="TradingView CFD Screener")
def query_cfd_screener(
    req: GenericScreenerRequest = GenericScreenerRequest(),
    screener_service: ScreenerService = Depends(get_screener_service)
):
    try:
        return screener_service.query_multi_asset("cfd", req)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
