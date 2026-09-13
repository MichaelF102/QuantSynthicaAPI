"""Valuation API endpoints."""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from quant_synthica_api.core.security import verify_api_key
from quant_synthica_api.services.container import container
from quant_synthica_api.services.valuation_service import ValuationService

router = APIRouter(prefix="/valuation", tags=["Valuation Models"], dependencies=[Depends(verify_api_key)])


def get_valuation_service() -> ValuationService:
    return container.valuation_service


class DCFRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g. RELIANCE, AAPL)")
    growth_rate: Optional[float] = Field(None, description="Projected annual FCF growth rate (e.g. 0.12 for 12%)")
    discount_rate: Optional[float] = Field(None, description="Discount rate / WACC (e.g. 0.10 for 10%)")
    terminal_growth_rate: Optional[float] = Field(None, description="Terminal perpetual growth rate (e.g. 0.03 for 3%)")
    years: int = Field(5, description="Projection years (default 5)")
    exit_multiple: Optional[float] = Field(None, description="Optional EV/EBITDA or EV/FCF exit multiple")


@router.get("/{symbol}")
def get_valuation_overview(
    symbol: str,
    service: ValuationService = Depends(get_valuation_service),
) -> Dict[str, Any]:
    """Return comprehensive valuation overview combining DCF, Piotroski F-Score, Altman Z-Score, and Graham Number."""
    return service.get_valuation_overview(symbol)


@router.post("/dcf")
def run_dcf_valuation(
    req: DCFRequest,
    service: ValuationService = Depends(get_valuation_service),
) -> Dict[str, Any]:
    """Execute custom Discounted Cash Flow (DCF) model with custom growth rates, discount rate and terminal assumptions."""
    return service.run_dcf(
        symbol_input=req.symbol,
        growth_rate=req.growth_rate,
        discount_rate=req.discount_rate,
        terminal_growth_rate=req.terminal_growth_rate,
        years=req.years,
        exit_multiple=req.exit_multiple,
    )


@router.get("/piotroski/{symbol}")
def get_piotroski_f_score(
    symbol: str,
    service: ValuationService = Depends(get_valuation_service),
) -> Dict[str, Any]:
    """Calculate the 9-point Piotroski F-Score for financial strength and accounting health."""
    return service.get_piotroski_score(symbol)


@router.get("/altman-z/{symbol}")
def get_altman_z_score(
    symbol: str,
    service: ValuationService = Depends(get_valuation_service),
) -> Dict[str, Any]:
    """Calculate the Altman Z-Score for bankruptcy distress prediction and credit health."""
    return service.get_altman_z_score(symbol)


@router.get("/graham/{symbol}")
def get_graham_valuation(
    symbol: str,
    service: ValuationService = Depends(get_valuation_service),
) -> Dict[str, Any]:
    """Calculate Benjamin Graham Number and Net-Net Working Capital valuation."""
    return service.get_graham_valuation(symbol)
