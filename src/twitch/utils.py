from src.database import async_session_maker
from sqlalchemy import select, delete
from src.playlist.models import Playlist


async def get_track_url():
    async with async_session_maker() as session:
        track = select(Playlist).limit(1)
        data = await session.execute(track)
        res_data = data.scalar_one_or_none()
        if res_data is not None:
            data_remove = delete(Playlist).where(Playlist.id == res_data.id)
            await session.execute(data_remove)
            await session.commit()
    return res_data
