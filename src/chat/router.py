import asyncio

from typing import List
from aioredis.client import PubSub, Redis

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.chat.models import Message
from src.chat.schemas import MessageModel
from src.database import get_async_session, create_redis_pool

from src.settings.ws_conf import ConnectionManager

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


manager = ConnectionManager()
channel_name = 'websocket_chat_channel'


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
    await redis_connector(websocket, client_id)


async def redis_connector(
    websocket: WebSocket, client_id: int
):
    async def consumer_handler(conn: Redis, ws: WebSocket):
        try:
            while True:
                message = await ws.receive_text()
                if message:
                    await conn.publish("chat:c", message)
        except WebSocketDisconnect as exc:
            # TODO this needs handling better
            print(exc)

    async def producer_handler(pubsub: PubSub, ws: WebSocket):
        await pubsub.subscribe("chat:c")
        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    data = message["data"].decode('utf-8')
                    await manager.broadcast(f"Client #{client_id} says: {data}", ws, add_to_db=True)
        except Exception as exc:
            # TODO this needs handling better
            print(exc)

    conn = await create_redis_pool()
    pubsub = conn.pubsub()

    consumer_task = consumer_handler(conn=conn, ws=websocket)
    producer_task = producer_handler(pubsub=pubsub, ws=websocket)
    done, pending = await asyncio.wait(
        [consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED,
    )
    print(f"Done task: {done}")
    for task in pending:
        print(f"Canceling task: {task}")
        task.cancel()
