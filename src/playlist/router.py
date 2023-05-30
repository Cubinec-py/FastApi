import aioredis

from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from pytube import extract, YouTube

from src.database import get_async_session, create_redis_pool
from src.playlist.models import Playlist
from src.playlist.schemas import PlaylistCreate
from src.twitch.utils import next_track as celery_next_track, get_tracks_count

from src.settings.settings import Settings, templates
from src.settings.ws_conf import ConnectionManager

router = APIRouter(
    prefix="/playlist",
    tags=["Playlist"]
)

ws_manager = ConnectionManager()
channel_name = 'websocket_channel'


@router.get("")
async def get_playlist(session: AsyncSession = Depends(get_async_session)):
    query = select(Playlist)
    data = await session.execute(query)
    return {"status": "success", "data": data.mappings().all()}


@router.post("")
async def add_to_playlist(playlist: PlaylistCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(Playlist).values(**playlist.dict())
    await session.execute(stmt)
    await session.commit()
    if await get_tracks_count() == 1:
        await celery_next_track()
    return {"status": "201 success"}


@router.get("/player")
async def get_video_page(request: Request):
    return templates.TemplateResponse(
        "playlist/player.html",
        {
            "request": request,
            "API_KEY": Settings.YOUTUBE_API_KEY,
            "video_id": '',
            "WS_URL": Settings.WS_URL,
        })


@router.post("/song_add")
async def play_new_video(url: str):
    video_id = extract.video_id(url)
    age_permission = extract.is_age_restricted(url)
    private = extract.is_private(url)
    lenth = YouTube(url)
    redis = await create_redis_pool()
    await redis.publish(channel_name, video_id)
    return {
        "message": f"New video started: {video_id}",
        "video_lenth": lenth.length,
        "data": [age_permission, private]
    }


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    redis = await create_redis_pool()
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel_name)
    await ws_manager.connect(websocket)
    try:
        while True:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = message["data"].decode()
                    await websocket.send_text(data)
            data = await websocket.receive_text()
            await redis.publish(channel_name, data)
            if str(data) == 'video_ended':
                redis = await aioredis.from_url(Settings.REDIS_URL)
                await redis.set('video_url', 'False')
                await celery_next_track()
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    finally:
        await pubsub.unsubscribe(channel_name)
        await pubsub.close()
