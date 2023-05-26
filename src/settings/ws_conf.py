from fastapi import WebSocket
from sqlalchemy import insert, delete, select

from src.database import async_session_maker
from src.chat.models import Message


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, add_to_db: bool = False):
        await websocket.accept()
        host = websocket.scope["client"][0]
        port = websocket.scope["client"][1]
        if add_to_db:
            await self.add_host_port_to_database(f"ws://{host}:{int(port) + 1}/api/v1/playlist/ws")
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket, remove_from_db: bool = False):
        print('Disconnected')
        if remove_from_db:
            await self.remove_host_port_from_database()
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str, add_to_db: bool = False):
        if add_to_db:
            await self.add_messages_to_database(message)
        for connection in self.active_connections:
            await connection.send_text(message)

    @staticmethod
    async def add_messages_to_database(message: str):
        async with async_session_maker() as session:
            stmt = insert(Message).values(message=message)
            await session.execute(stmt)
            await session.commit()

    @staticmethod
    async def add_host_port_to_database(data: str):
        async with async_session_maker() as session:
            stmt = insert(Message).values(message=data)
            await session.execute(stmt)
            await session.commit()

    @staticmethod
    async def remove_host_port_from_database():
        async with async_session_maker() as session:
            smt = delete(Message)
            await session.execute(smt)
            await session.commit()
