from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session, create_redis_pool
from src.playlist.models import Playlist
from src.playlist.schemas import PlaylistCreate, VideoUrl
from src.twitch.utils import next_track as celery_next_track, get_tracks_count, get_track_id, get_track_length

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
            "url_ended": f'{Settings.SERVER_URL}/api/v1/playlist/video_ended?ended=true',
            "WS_URL": Settings.WS_URL,
        })


@router.post("/song_add")
async def play_new_video(url: VideoUrl):
    video_id = get_track_id(url.dict()['video_url'])
    length = await get_track_length(url.dict()['video_url'])
    redis = await create_redis_pool()
    await redis.publish(channel_name, video_id)
    return {
        "message": f'New video started: {video_id}',
        "video_length": length,
    }


@router.post("/video_ended")
async def video_ended(ended: bool):
    if ended:
        await celery_next_track(ended=True)
        return {"status": "201 success"}
    return {"status": "ERROR invalid data"}


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
                    data_send = message["data"].decode()
                    await ws_manager.broadcast(data_send)
            data = await websocket.receive_text()
            await redis.publish(channel_name, data)
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    finally:
        await pubsub.unsubscribe(channel_name)
        await pubsub.close()
