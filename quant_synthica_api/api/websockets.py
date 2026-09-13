"""WebSocket Live Tick & Quote Streaming endpoint."""

import asyncio
import json
import logging
import time
from typing import Dict, Set, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from quant_synthica_api.services.container import container
from quant_synthica_api.services.symbol_resolver import SymbolResolver

logger = logging.getLogger("quantsynthica.websocket")

ws_router = APIRouter(prefix="/ws", tags=["Live WebSockets"])


class ConnectionManager:
    def __init__(self):
        # Map websocket -> set of subscribed symbols
        self.active_connections: Dict[WebSocket, Set[str]] = {}
        self._lock = asyncio.Lock()
        self._broadcaster_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections[websocket] = set()
            if self._broadcaster_task is None or self._broadcaster_task.done():
                self._broadcaster_task = asyncio.create_task(self._broadcast_loop())

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active_connections:
                del self.active_connections[websocket]
            if len(self.active_connections) == 0 and self._broadcaster_task:
                self._broadcaster_task.cancel()
                self._broadcaster_task = None

    def subscribe(self, websocket: WebSocket, symbols: list[str]) -> list[str]:
        if websocket in self.active_connections:
            resolved_symbols = []
            for s in symbols:
                try:
                    res = SymbolResolver.resolve(s)
                    self.active_connections[websocket].add(res.canonical)
                    resolved_symbols.append(res.canonical)
                except Exception:
                    self.active_connections[websocket].add(s.upper())
                    resolved_symbols.append(s.upper())
            return resolved_symbols
        return []

    def unsubscribe(self, websocket: WebSocket, symbols: list[str]):
        if websocket in self.active_connections:
            for s in symbols:
                self.active_connections[websocket].discard(s.upper())

    async def _broadcast_loop(self):
        """Periodically broadcast latest quotes for subscribed symbols."""
        while True:
            try:
                await asyncio.sleep(3.0)  # Stream tick update interval
                async with self._lock:
                    if not self.active_connections:
                        break
                    
                    # Gather unique symbols
                    all_symbols = set()
                    for syms in self.active_connections.values():
                        all_symbols.update(syms)

                if not all_symbols:
                    continue

                # Fetch quotes
                quotes_cache = {}
                for sym in all_symbols:
                    try:
                        q = container.market_service.get_quote(sym)
                        if q and q.data:
                            quotes_cache[sym] = {
                                "symbol": sym,
                                "price": q.data.price,
                                "change": q.data.change,
                                "change_percent": q.data.change_percent,
                                "volume": q.data.volume,
                                "timestamp": time.time(),
                            }
                    except Exception as e:
                        logger.debug(f"Tick fetch error for {sym}: {e}")

                # Dispatch to connected clients
                async with self._lock:
                    for ws, client_syms in list(self.active_connections.items()):
                        relevant = [quotes_cache[s] for s in client_syms if s in quotes_cache]
                        if relevant:
                            try:
                                await ws.send_json({
                                    "type": "tick",
                                    "data": relevant,
                                    "timestamp": time.time(),
                                })
                            except Exception:
                                pass
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"WebSocket broadcaster error: {e}")
                await asyncio.sleep(1.0)


manager = ConnectionManager()


@ws_router.websocket("/quotes")
async def websocket_quotes_endpoint(websocket: WebSocket):
    """Live quotes WebSocket connection.

    Protocol:
    - Send: `{"action": "subscribe", "symbols": ["RELIANCE", "AAPL"]}`
    - Send: `{"action": "unsubscribe", "symbols": ["AAPL"]}`
    - Send: `{"action": "ping"}`
    - Receive: `{"type": "tick", "data": [...]}` or `{"action": "pong"}`
    """
    await manager.connect(websocket)
    try:
        # Welcome message
        await websocket.send_json({
            "type": "connection_ack",
            "message": "Connected to QuantSynthica Live Quotes Stream",
            "supported_actions": ["subscribe", "unsubscribe", "ping"],
        })

        while True:
            text_data = await websocket.receive_text()
            try:
                data = json.loads(text_data)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON format"})
                continue

            action = data.get("action", "").lower()

            if action == "subscribe":
                syms = data.get("symbols", [])
                if isinstance(syms, str):
                    syms = [syms]
                subscribed = manager.subscribe(websocket, syms)

                # Send immediate snapshot
                snapshot = []
                for s in subscribed:
                    try:
                        q = container.market_service.get_quote(s)
                        if q and q.data:
                            snapshot.append({
                                "symbol": s,
                                "price": q.data.price,
                                "change": q.data.change,
                                "change_percent": q.data.change_percent,
                                "volume": q.data.volume,
                            })
                    except Exception:
                        pass

                await websocket.send_json({
                    "type": "subscribed",
                    "symbols": list(manager.active_connections.get(websocket, [])),
                    "snapshot": snapshot,
                })

            elif action == "unsubscribe":
                syms = data.get("symbols", [])
                if isinstance(syms, str):
                    syms = [syms]
                manager.unsubscribe(websocket, syms)
                await websocket.send_json({
                    "type": "unsubscribed",
                    "symbols": list(manager.active_connections.get(websocket, [])),
                })

            elif action == "ping":
                await websocket.send_json({
                    "action": "pong",
                    "timestamp": time.time(),
                })

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown action '{action}'. Use 'subscribe', 'unsubscribe', or 'ping'.",
                })

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket client error: {e}")
        await manager.disconnect(websocket)
