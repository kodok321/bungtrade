import asyncio
import json
import logging
from fastapi import WebSocket, WebSocketDisconnect
import aiohttp

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


async def binance_ws_proxy(websocket: WebSocket, symbol: str, stream: str = "ticker"):
    await manager.connect(websocket)
    symbol_lower = symbol.lower()

    if stream == "kline":
        ws_url = f"wss://stream.binance.com:9443/ws/{symbol_lower}@kline_1m"
    elif stream == "depth":
        ws_url = f"wss://stream.binance.com:9443/ws/{symbol_lower}@depth20@100ms"
    elif stream == "trade":
        ws_url = f"wss://stream.binance.com:9443/ws/{symbol_lower}@trade"
    else:
        ws_url = f"wss://stream.binance.com:9443/ws/{symbol_lower}@ticker"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as binance_ws:
                async def forward_binance():
                    async for msg in binance_ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            await websocket.send_json(data)
                        elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                            break

                async def listen_client():
                    try:
                        while True:
                            await websocket.receive_text()
                    except WebSocketDisconnect:
                        pass

                await asyncio.gather(forward_binance(), listen_client(), return_exceptions=True)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)
