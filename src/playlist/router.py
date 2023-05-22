import asyncio
import websockets

from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from pytube import extract
from fastapi.templating import Jinja2Templates
from pathlib import Path

from src.database import get_async_session
from src.playlist.models import Playlist
from src.playlist.schemas import PlaylistCreate, VideoUrl
from src.chat.router import manager

from src.settings.settings import Settings

router = APIRouter(
    prefix="/playlist",
    tags=["Playlist"]
)

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
active_connections = []
current_video_id = '1IFnKHhBv7w'


@router.get("")
async def get_playlist(session: AsyncSession = Depends(get_async_session)):
    query = select(Playlist)
    data = await session.execute(query)
    return {"status": "success", "data": data.mappings().all()}


@router.post("")
async def get_playlist(playlist: PlaylistCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(Playlist).values(**playlist.dict())
    await session.execute(stmt)
    await session.commit()
    return {"status": "201 success"}


@router.get("/player")
async def get_video_page(request: Request):
    return templates.TemplateResponse(
        "playlist/player.html",
        {
            "request": request,
            "video_id": current_video_id,
            "WS_URL": Settings.WS_URL,
        })


@router.post("/song_add")
async def play_new_video(url: str):
    global active_connections
    video_id = extract.video_id(url)
    print('active_connections', active_connections)
    for client in active_connections:
        await client.send_text(video_id)
    # url = f"{Settings.WS_URL}/api/v1/playlist/ws"
    # async with websockets.connect(url) as websocket:
    #     active_connections.append(websocket)
    #     await websocket.send(f"{video_id}")
    #     ans = await websocket.recv()
    #     await asyncio.sleep(1)
    return {"message": "New video started: {}".format(video_id)}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global active_connections
    await manager.connect(websocket)
    try:
        while True:
            active_connections.append(websocket)
            print(active_connections)
            data = await websocket.receive_text()
            print(f"Received data from client: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        active_connections.remove(websocket)

