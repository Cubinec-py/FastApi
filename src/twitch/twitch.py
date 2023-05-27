import os
import re
import twitchio
import aiohttp
import pytube

from pytube import YouTube
from twitchio.ext import commands, pubsub
from dotenv import load_dotenv
from typing import List

from src.settings.settings import Settings
from src.tasks.tasks import skip_track
from src.twitch.utils import get_track_url

load_dotenv()


my_token = os.environ.get('TWITCH_CHANNEL_ACCESS_TOKEN')
INIT_CHANNELS = ["cubinec2012"]
users_oauth_token = os.environ.get('TWITCH_CHANNEL_ACCESS_TOKEN')
users_channel_id = 39312917
reward_id = 0
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

    @client.event()
    async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
        if event.reward.title == 'Заказать Трек':
            link = event.input
            reward_redemptions_list = await event.reward.get_redemptions(token=users_oauth_token, status='UNFULFILLED')
            channel = bot.get_channel('cubinec2012')
            if re.match('^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?' \
                        'v=|embed\/|v\/)?)([\w\-]+)(\S+)?$', link):
                track = YouTube(link)
                url = f'{Settings.SERVER_URL}/api/v1/playlist'
                data = {'track': link, "length": track.length}
                try:
                    any(stream.is_live for stream in track.streams)
                except pytube.exceptions.LiveStreamError:
                    await reward_redemptions_list[-1].refund(token=users_oauth_token)
                    await channel.send(f'@{event.user.name} Только треки, не онлайн стримы!')
                    return
                if track.length > 300:
                    await reward_redemptions_list[-1].refund(token=users_oauth_token)
                    await channel.send(f'@{event.user.name} Трек {track.streams[0].title} слишком длинный, не длинее 5 минут!')
                    return
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=data) as resp:
                        await resp.text()
                await reward_redemptions_list[-1].fulfill(token=users_oauth_token)
                await channel.send(f'@{event.user.name} Трек {track.streams[0].title} успешно добавлен в плейлист!')
            else:
                await reward_redemptions_list[-1].refund(token=users_oauth_token)
                await channel.send(f'@{event.user.name} только youtube ссылки PixelBob')
        elif event.reward.title == 'Скип':
            pass

    @commands.command(name='скип')
    async def skip_track(self, ctx: commands.Context):
        if ctx.author.name == "cubinec2012":
            self.skip_count = 0
            data = await get_track_url()
            track = YouTube(data.track)
            skip_track.delay(data.track)
            await ctx.channel.send(f'@{ctx.author.name} Скипнул на {track.streams[0].title}!')
        elif self.skip_count < 5 and ctx.author.name not in self.users_votes_skip:
            self.users_votes_skip.append(ctx.author.name)
            self.skip_count += 1
            await ctx.channel.send(f'До скипа трека осталось - {5 - self.skip_count}/5')
        elif ctx.author.name in self.users_votes_skip:
            await ctx.channel.send(f'@{ctx.author.name} Ты уже проголосовал!')
        elif self.skip_count > 4 and ctx.author.name not in self.users_votes_skip:
            self.users_votes_skip.clear()
            self.skip_count = 0
            data = await get_track_url()
            track = YouTube(data.track)
            skip_track.delay(data.track)
            await ctx.channel.send(f'Трек успешно скипнут на {track.streams[0].title}!')

    async def event_ready(self) -> None:
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")


bot = Bot()


async def main():
    topic = [pubsub.channel_points(users_oauth_token)[users_channel_id]]
    await client.pubsub.subscribe_topics(topic)
    print('Starting twitch client ...')
    await client.start()


if __name__ == "__main__":
    client.loop.create_task(main())
    bot.run()
    client.loop.run_forever()
