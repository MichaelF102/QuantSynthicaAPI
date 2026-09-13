"""Tests for Excel and HTML report generation endpoints."""

import io
import openpyxl
from fastapi.testclient import TestClient
from quant_synthica_api.main import app

client = TestClient(app)
API_KEY_HEADER = {"X-API-Key": "dev_test_api_key_12345"}


def test_api_download_excel_model():
    resp = client.get("/api/v1/reports/excel/RELIANCE", headers=API_KEY_HEADER)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    # Read binary bytes with openpyxl to verify valid workbook
    wb = openpyxl.load_workbook(io.BytesIO(resp.content))
    sheet_names = wb.sheetnames
    assert "Company Overview" in sheet_names
    assert "Valuation Models" in sheet_names
    assert "Historical Prices" in sheet_names

    ws_overview = wb["Company Overview"]
    assert "RELIANCE" in str(ws_overview["A1"].value)


def test_api_get_tearsheet_html():
    resp = client.get("/api/v1/reports/tearsheet/RELIANCE", headers=API_KEY_HEADER)
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    text = resp.text
    assert "<title>QuantSynthica Tearsheet - RELIANCE.NS</title>" in text or "QuantSynthica Tearsheet" in text
    assert "Valuation & Solvency Overview" in text
