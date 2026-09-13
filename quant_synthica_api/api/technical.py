from fastapi import APIRouter, Depends, Query, HTTPException, status
from quant_synthica_api.schemas.quant import TechnicalResponse
from quant_synthica_api.services.quant_service import QuantService
from quant_synthica_api.services.container import get_quant_service
from quant_synthica_api.core.security import verify_api_key

router = APIRouter(prefix="/technical", tags=["Technical Analysis"], dependencies=[Depends(verify_api_key)])

@router.get("/{symbol}", response_model=TechnicalResponse, summary="Get technical indicators for symbol")
def get_technical_indicators(
    symbol: str,
    period: str = Query(default="1y", description="Data period for calculation e.g. 6mo, 1y, 2y"),
    quant_service: QuantService = Depends(get_quant_service)
):
    try:
        return quant_service.get_technical(symbol, period=period)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
