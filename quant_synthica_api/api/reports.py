"""Reports and Factsheet Export API endpoints."""

from fastapi import APIRouter, Depends, Response
from fastapi.responses import HTMLResponse

from quant_synthica_api.core.security import verify_api_key
from quant_synthica_api.services.container import container
from quant_synthica_api.services.report_service import ReportService
from quant_synthica_api.services.symbol_resolver import SymbolResolver

router = APIRouter(prefix="/reports", tags=["Institutional Reports & Exports"], dependencies=[Depends(verify_api_key)])


def get_report_service() -> ReportService:
    return container.report_service


@router.get("/excel/{symbol}")
def download_excel_model(
    symbol: str,
    service: ReportService = Depends(get_report_service),
):
    """Download multi-tab formatted Excel financial model workbook (.xlsx)."""
    resolved = SymbolResolver.resolve(symbol)
    content = service.generate_excel_workbook(symbol)
    headers = {
        "Content-Disposition": f'attachment; filename="{resolved.canonical}_financial_model.xlsx"',
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    return Response(content=content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)


@router.get("/tearsheet/{symbol}", response_class=HTMLResponse)
def get_institutional_tearsheet(
    symbol: str,
    service: ReportService = Depends(get_report_service),
):
    """View printable institutional factsheet / tearsheet HTML with key KPIs, valuation and risk analytics."""
    return service.generate_tearsheet_html(symbol)
