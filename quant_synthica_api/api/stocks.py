from fastapi import APIRouter, Depends, HTTPException, status
from quant_synthica_api.schemas.stock_profile import StockProfileResponse
from quant_synthica_api.services.stock_profile_service import StockProfileService
from quant_synthica_api.services.container import get_stock_profile_service
from quant_synthica_api.core.security import verify_api_key

router = APIRouter(prefix="/stocks", tags=["Stock Profile"], dependencies=[Depends(verify_api_key)])

@router.get("/{symbol}", response_model=StockProfileResponse, summary="Get unified 360° stock profile")
def get_unified_stock_profile(
    symbol: str,
    profile_service: StockProfileService = Depends(get_stock_profile_service)
):
    try:
        return profile_service.get_stock_profile(symbol)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
