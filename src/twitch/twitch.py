import os
import re
from typing import List

import aioredis
import twitchio
from dotenv import load_dotenv
from twitchio.ext import commands, pubsub, routines

from src.settings.settings import Settings
from src.twitch.utils import \
    get_answer, start_current_track, check_stream_or_not, get_track_title, get_track_length, add_track_to_playlist

load_dotenv()

my_token = os.environ.get('TWITCH_CHANNEL_ACCESS_TOKEN')
reward_add_id = os.environ.get('TWITCH_REWARD_ADD_ID')
reward_skip_id = os.environ.get('TWITCH_REWARD_SKIP_ID')
INIT_CHANNELS = ['cubinec2012']
users_oauth_token = os.environ.get('TWITCH_CHANNEL_ACCESS_TOKEN')
users_channel_id = int(os.environ.get('USER_CHANNEL_ID'))
client = twitchio.Client(token=my_token, client_secret=os.environ.get('TWITCH_CLIENT_SECRET'))
client.pubsub = pubsub.PubSubPool(client)


class Bot(commands.Bot):
    def __init__(self):
        self.skip_count: int = 5
        self.users_votes_skip: List[int] = []
        super().__init__(
            token=my_token,
            prefix="!",
            initial_channels=INIT_CHANNELS,
        )

    @commands.command(name='скип')
    async def skip_track(self, ctx: commands.Context):
        if ctx.author.name == "cubinec2012":
            self.users_votes_skip.clear()
            self.skip_count = 0
            await get_answer(ctx)
        elif self.skip_count < 5 and ctx.author.name not in self.users_votes_skip:
            self.users_votes_skip.append(ctx.author.name)
            self.skip_count += 1
            await ctx.channel.send(f'До скипа трека осталось - {5 - self.skip_count}/5')
        elif ctx.author.name in self.users_votes_skip:
            await ctx.channel.send(f'@{ctx.author.name} Ты уже проголосовал!')
        elif self.skip_count > 4 and ctx.author.name not in self.users_votes_skip:
            self.users_votes_skip.clear()
            self.skip_count = 0
            await get_answer(ctx)

    @commands.command(name='трек')
    async def track_info(self, ctx: commands.Context):
        redis = await aioredis.from_url(Settings.REDIS_URL)
        track_url = await redis.get('video_url')
        if track_url and track_url.decode('utf-8') != 'False':
            title = await get_track_title(track_url.decode('utf-8'))
            await ctx.channel.send(f'Текущий трек: {title}')
        else:
            await ctx.channel.send('Сейчас ни один трек не воспроизводится!')

    @commands.command(name='старт')
    async def track_start(self, ctx: commands.Context):
        if ctx.author.name == "cubinec2012":
            await start_current_track(ctx)
        else:
            await ctx.channel.send(f'@{ctx.author.name} У тебя нет прав PixelBob')

    @routines.routine(minutes=15)
    async def info(self):
        channel = bot.get_channel('cubinec2012')
        await channel.send(
            'За балы канала доступен заказ, скип треков! '
            'Так же, доступны команды: !трек, !скип в чате!'
        )

    async def event_ready(self) -> None:
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")
        self.info.start()


bot = Bot()


@client.event()
async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
    channel = bot.get_channel('cubinec2012')
    if event.reward.id == reward_add_id:
        yt_regex_url = re.compile(
            r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$'
        )
        link = event.input
        reward_redemptions_list = await event.reward.get_redemptions(token=users_oauth_token, status='UNFULFILLED')
        if yt_regex_url.match(link):
            title = await get_track_title(link)
            if await check_stream_or_not(link):
                await reward_redemptions_list[-1].refund(token=users_oauth_token)
                await channel.send(f'@{event.user.name} Только треки, не онлайн стримы!')
                return

            if await get_track_length(link) > 300:
                await reward_redemptions_list[-1].refund(token=users_oauth_token)
                await channel.send(
                    f'@{event.user.name} Трек {title} слишком длинный, не длинее 5 минут!'
                )
                return
            await add_track_to_playlist(link)
            await reward_redemptions_list[-1].fulfill(token=users_oauth_token)
            await channel.send(f'@{event.user.name} Трек {title} успешно добавлен в плейлист!')
        else:
            await reward_redemptions_list[-1].refund(token=users_oauth_token)
            await channel.send(f'@{event.user.name} только youtube ссылки PixelBob')
    elif event.reward.id == reward_skip_id:
        reward_redemptions_list = await event.reward.get_redemptions(token=users_oauth_token, status='UNFULFILLED')
        await reward_redemptions_list[-1].fulfill(token=users_oauth_token)
        await get_answer(event, channel, reward=True)


async def main():
    topic = [pubsub.channel_points(users_oauth_token)[users_channel_id]]
    await client.pubsub.subscribe_topics(topic)
    print('Starting twitch client ...')
    await client.start()


if __name__ == "__main__":
    client.loop.create_task(main())
    bot.run()
    client.loop.run_forever()
