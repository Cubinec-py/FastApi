from src.database import async_session_maker, create_redis_pool
from sqlalchemy import select, delete, func
from src.playlist.models import Playlist
from src.tasks.tasks import skip_track


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


async def get_tracks_count():
    async with async_session_maker() as session:
        query = select(func.count()).select_from(Playlist)
        data = await session.execute(query)
        track_count = data.scalar_one_or_none()
        await session.commit()
    return track_count


async def next_track():
    redis = await create_redis_pool()
    r = await redis.get('video_url')
    if r is None or r.decode('utf-8') == 'False':
        data = await get_track_url()
        if data is not None:
            skip_track.delay(f'{data.track}')
            return data.track
        await redis.set('video_url', 'False')
        return False
    return False


async def get_answer(ctx, channel=None, reward: bool = False):
    data = await get_track_url()
    if data is not None:
        from pytube import YouTube
        track = YouTube(data.track)
        skip_track.delay(f'{data.track}')
        if reward:
            await channel.send(f'Трек скипнут на {track.streams[0].title}!')
        else:
            await ctx.channel.send(f'Трек скипнут на {track.streams[0].title}!')
    else:
        if reward:
            await channel.send(f'В плейлисте больше нет треков!')
        else:
            await ctx.channel.send(f'В плейлисте больше нет треков!')


async def start_current_track(ctx):
    from pytube import YouTube
    redis = await create_redis_pool()
    r = await redis.get('video_url')
    if r is not None or r.decode('utf-8') != 'False':
        track_url = r.decode('utf-8')
        skip_track.delay(f'{track_url}')
        track = YouTube(track_url)
        await ctx.channel.send(f'Трек {track.streams[0].title} запущен')
    elif r is None or r.decode('utf-8') == 'False':
        track_url = await next_track()
        if track_url:
            track = YouTube(track_url)
            await ctx.channel.send(f'Трек {track.streams[0].title} запущен')
        else:
            await ctx.channel.send(f'Запускать нечего')
    await ctx.channel.send(f'Что-то пошло не так')
