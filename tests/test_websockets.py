"""Tests for WebSocket quote streaming."""

import json
from fastapi.testclient import TestClient
from quant_synthica_api.main import app

client = TestClient(app)


def test_websocket_ping_pong():
    with client.websocket_connect("/api/v1/ws/quotes") as ws:
        # Check welcome ack
        ack = ws.receive_json()
        assert ack["type"] == "connection_ack"

        # Send ping
        ws.send_text(json.dumps({"action": "ping"}))
        pong = ws.receive_json()
        assert pong["action"] == "pong"
        assert "timestamp" in pong


def test_websocket_subscribe():
    with client.websocket_connect("/api/v1/ws/quotes") as ws:
        ack = ws.receive_json()
        assert ack["type"] == "connection_ack"

        # Subscribe to RELIANCE
        ws.send_text(json.dumps({"action": "subscribe", "symbols": ["RELIANCE"]}))
        sub_resp = ws.receive_json()
        assert sub_resp["type"] == "subscribed"
        assert "RELIANCE.NS" in sub_resp["symbols"] or "RELIANCE" in sub_resp["symbols"]
