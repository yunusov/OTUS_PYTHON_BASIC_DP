from __future__ import annotations

from typing import Dict
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self) -> None:
        self.connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[user_id] = websocket

    def disconnect(self, user_id: int) -> None:
        self.connections.pop(user_id, None)

    async def send_personal(self, user_id: int, payload: dict) -> bool:
        ws = self.connections.get(user_id)
        if not ws:
            return False
        try:
            await ws.send_json(payload)
            return True
        except Exception:
            self.disconnect(user_id)
            return False


ws_manager = WebSocketManager()
