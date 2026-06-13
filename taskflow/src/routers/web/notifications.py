from fastapi import APIRouter, WebSocket

from src.core.ws_manager import ws_manager

router = APIRouter(prefix="/ws", tags=["ws"])


@router.websocket("/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: int):
    await ws_manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        ws_manager.disconnect(user_id)
