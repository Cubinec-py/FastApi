from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.chat.models import Message
from src.chat.schemas import MessageModel
from src.database import get_async_session

from src.settings.ws_conf import ConnectionManager

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


manager = ConnectionManager()


@router.get("/last_messages")
async def get_last_messages(
    session: AsyncSession = Depends(get_async_session),
) -> List[MessageModel]:
    query = select(Message).order_by(Message.id.desc()).limit(5)
    messages = await session.execute(query)
    return messages.scalars().all()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client #{client_id} says: {data}", add_to_db=True)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat", add_to_db=False)
