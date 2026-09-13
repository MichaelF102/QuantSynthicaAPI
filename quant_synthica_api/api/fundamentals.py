from fastapi import APIRouter, Depends, Query, HTTPException, status
from quant_synthica_api.schemas.fundamentals import (
    UnifiedFundamentalsResponse, FinancialStatementResponse,
    RatiosResponse, ShareholdingResponse, HoldersResponse,
    InsiderTransactionsResponse, SustainabilityResponse,
    PeersResponse, CorporateAnalysisResponse, DocumentsResponse
)
from quant_synthica_api.services.fundamentals_service import FundamentalsService
from quant_synthica_api.services.container import get_fundamentals_service
from quant_synthica_api.core.security import verify_api_key

router = APIRouter(prefix="/fundamentals", tags=["Fundamentals"], dependencies=[Depends(verify_api_key)])

@router.get("/{symbol}", response_model=UnifiedFundamentalsResponse, summary="Get unified company fundamentals")
def get_company_fundamentals(
    symbol: str,
    fundamentals_service: FundamentalsService = Depends(get_fundamentals_service)
):
    try:
        return fundamentals_service.get_unified_fundamentals(symbol)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/income-statement", response_model=FinancialStatementResponse, summary="Get income statement / P&L")
def get_income_statement(
    symbol: str,
    fundamentals_service: FundamentalsService = Depends(get_fundamentals_service)
):
    try:
        return fundamentals_service.get_income_statement(symbol)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/balance-sheet", response_model=FinancialStatementResponse, summary="Get balance sheet")
def get_balance_sheet(
    symbol: str,
    fundamentals_service: FundamentalsService = Depends(get_fundamentals_service)
):
    try:
        return fundamentals_service.get_balance_sheet(symbol)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/cash-flow", response_model=FinancialStatementResponse, summary="Get cash flow statement")
def get_cash_flow(
    symbol: str,
    fundamentals_service: FundamentalsService = Depends(get_fundamentals_service)
):
    try:
        return fundamentals_service.get_cash_flow(symbol)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/ratios", response_model=RatiosResponse, summary="Get valuation and financial ratios")
def get_ratios(
    symbol: str,
    fundamentals_service: FundamentalsService = Depends(get_fundamentals_service)
):
    try:
        return fundamentals_service.get_ratios(symbol)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/shareholding", response_model=ShareholdingResponse, summary="Get shareholding pattern")
def get_shareholding(
    symbol: str,
    fundamentals_service: FundamentalsService = Depends(get_fundamentals_service)
):
    try:
        return fundamentals_service.get_shareholding(symbol)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# --- Extended Fundamentals Endpoints ---

@router.get("/{symbol}/institutional-holders", response_model=HoldersResponse, summary="Get top institutional shareholders")
def get_institutional_holders(
    symbol: str,
    fundamentals_service: FundamentalsService = Depends(get_fundamentals_service)
):
    try:
        return fundamentals_service.get_holders(symbol, holder_type="institutional")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/mutual-funds", response_model=HoldersResponse, summary="Get mutual fund shareholders")
def get_mutual_fund_holders(
    symbol: str,
    fundamentals_service: FundamentalsService = Depends(get_fundamentals_service)
):
    try:
        return fundamentals_service.get_holders(symbol, holder_type="mutualfund")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/insider-transactions", response_model=InsiderTransactionsResponse, summary="Get insider buy/sell transactions")
def get_insider_transactions(
    symbol: str,
    fundamentals_service: FundamentalsService = Depends(get_fundamentals_service)
):
    try:
        return fundamentals_service.get_insider_transactions(symbol)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/sustainability", response_model=SustainabilityResponse, summary="Get ESG and sustainability risk ratings")
def get_sustainability_ratings(
    symbol: str,
    fundamentals_service: FundamentalsService = Depends(get_fundamentals_service)
):
    try:
        return fundamentals_service.get_sustainability(symbol)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/peers", response_model=PeersResponse, summary="Get industry peer comparison table (from Screener.in)")
def get_peers_comparison(
    symbol: str,
    fundamentals_service: FundamentalsService = Depends(get_fundamentals_service)
):
    try:
        return fundamentals_service.get_peers(symbol)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/analysis", response_model=CorporateAnalysisResponse, summary="Get pros and cons analysis (from Screener.in)")
def get_corporate_analysis(
    symbol: str,
    fundamentals_service: FundamentalsService = Depends(get_fundamentals_service)
):
    try:
        return fundamentals_service.get_analysis(symbol)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{symbol}/documents", response_model=DocumentsResponse, summary="Get concalls, presentations, annual reports (from Screener.in)")
def get_corporate_documents(
    symbol: str,
    limit: int = Query(default=20, ge=1, le=50),
    fundamentals_service: FundamentalsService = Depends(get_fundamentals_service)
):
    try:
        return fundamentals_service.get_documents(symbol, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
