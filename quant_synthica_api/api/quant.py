from fastapi import APIRouter, Depends, Query, HTTPException, status
from quant_synthica_api.schemas.quant import (
    ReturnsResponse, RiskResponse, VolatilityResponse, QuantSummaryResponse
)
from quant_synthica_api.services.quant_service import QuantService
from quant_synthica_api.services.container import get_quant_service
from quant_synthica_api.core.security import verify_api_key

router = APIRouter(prefix="/quant", tags=["Quantitative Analytics"], dependencies=[Depends(verify_api_key)])

@router.get("/{symbol}/returns", response_model=ReturnsResponse, summary="Get returns and CAGR metrics")
def get_quant_returns(
    symbol: str,
    period: str = Query(default="1y", description="History period e.g. 1y, 2y, 5y"),
    quant_service: QuantService = Depends(get_quant_service)
):
    try:
        return quant_service.get_returns(symbol, period=period)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/risk", response_model=RiskResponse, summary="Get risk metrics (Sharpe, Sortino, Max Drawdown, VaR)")
def get_quant_risk(
    symbol: str,
    period: str = Query(default="1y", description="History period e.g. 1y, 2y, 5y"),
    risk_free_rate: float = Query(default=0.06, description="Annual risk-free rate"),
    quant_service: QuantService = Depends(get_quant_service)
):
    try:
        return quant_service.get_risk(symbol, period=period, risk_free_rate=risk_free_rate)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/volatility", response_model=VolatilityResponse, summary="Get volatility metrics")
def get_quant_volatility(
    symbol: str,
    period: str = Query(default="1y", description="History period e.g. 1y, 2y"),
    quant_service: QuantService = Depends(get_quant_service)
):
    try:
        return quant_service.get_volatility(symbol, period=period)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/summary", response_model=QuantSummaryResponse, summary="Get complete quant summary (returns + risk + technical)")
def get_quant_summary(
    symbol: str,
    period: str = Query(default="1y", description="History period e.g. 1y, 2y"),
    risk_free_rate: float = Query(default=0.06, description="Annual risk-free rate"),
    quant_service: QuantService = Depends(get_quant_service)
):
    try:
        return quant_service.get_summary(symbol, period=period, risk_free_rate=risk_free_rate)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
