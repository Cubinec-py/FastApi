import aiohttp
import re
import isodate

from src.database import async_session_maker, create_redis_pool
from sqlalchemy import select, delete, func
from src.playlist.models import Playlist
from src.tasks.tasks import skip_track

from src.settings.settings import Settings

channel_name = 'websocket_channel'


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


async def next_track(ended: bool = False):
    redis = await create_redis_pool()
    r = await redis.get('video_url')
    if r is None or r.decode('utf-8') == 'False' or ended:
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
        title = await get_track_title(data.track)
        skip_track.delay(f'{data.track}')
        if reward:
            await channel.send(f'Трек скипнут на {title}!')
        else:
            await ctx.channel.send(f'Трек скипнут на {title}!')
    else:
        redis = await create_redis_pool()
        track_url = await redis.get('video_url')
        title = False
        if track_url is not None and track_url.decode('utf-8') != 'False':
            title = await get_track_title(track_url.decode('utf-8'))
        await redis.set('video_url', 'False')
        await redis.publish(channel_name, 'skip_track')
        if reward:
            if title:
                await channel.send(f'Трек {title} скипнут но в плейлисте больше нет треков!')
                return
            await channel.send('В плейлисте нет треков!')
        else:
            if title:
                await ctx.channel.send(f'Трек {title} скипнут но в плейлисте больше нет треков!')
                return
            await ctx.channel.send('В плейлисте нет треков!')


async def start_current_track(ctx):
    redis = await create_redis_pool()
    r = await redis.get('video_url')
    if r is not None and r.decode('utf-8') != 'False':
        track_url = r.decode('utf-8')
        skip_track.delay(f'{track_url}')
        title = await get_track_title(track_url)
        await ctx.channel.send(f'Трек {title} запущен')
    elif r is None or r.decode('utf-8') == 'False':
        track_url = await next_track()
        if track_url:
            title = await get_track_title(track_url)
            await ctx.channel.send(f'Трек {title} запущен')
        else:
            await ctx.channel.send('Запускать нечего')
    else:
        await ctx.channel.send('Что-то пошло не так')


async def get_track_info(url: str) -> dict:
    video_id = get_track_id(url)
    api_key = Settings.YOUTUBE_API_KEY
    url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={api_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{url}&part=snippet,contentDetails,statistics,status') as response:
            data = await response.json()
    return data


def get_track_id(url: str) -> str:
    regex = re.compile(r'(https?://)?(www\.)?(m\.)?(?:youtube\.com\/\S*(?:(?:\/e(?:mbed))?\/|watch\?(?:\S*?&?v\=))|youtu\.be\/)?(?P<id>[A-Za-z0-9\-=_]{11})')
    match = regex.match(url)
    video_id = match.group('id')
    return video_id


async def check_stream_or_not(url: str) -> bool:
    data = await get_track_info(url)
    stream = isodate.parse_duration(data['items'][0]['contentDetails']['duration']).seconds
    return True if stream <= 0 else False


async def get_track_title(url: str) -> str:
    data = await get_track_info(url)
    title = data['items'][0]['snippet']['title']
    return title


async def get_track_length(url: str) -> int:
    data = await get_track_info(url)
    duration = isodate.parse_duration(data['items'][0]['contentDetails']['duration']).seconds
    return int(duration)


async def add_track_to_playlist(video_url):
    url = f'{Settings.SERVER_URL}/api/v1/playlist'
    data = {'track': video_url}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as resp:
            status = resp.status
            await resp.json()
    return status
