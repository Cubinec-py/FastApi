import os
import re
import twitchio
import aiohttp

from pytube import YouTube
from twitchio.ext import pubsub
from twitchio.ext import commands, sounds
from dotenv import load_dotenv

from src.settings.settings import Settings

load_dotenv()


my_token = os.environ.get('TWITCH_CHANNEL_ACCESS_TOKEN')
INIT_CHANNELS = ["cubinec2012"]
users_oauth_token = os.environ.get('TWITCH_CHANNEL_ACCESS_TOKEN')
users_channel_id = 39312917
client = twitchio.Client(token=my_token, client_secret=os.environ.get('TWITCH_CLIENT_SECRET'))
client.pubsub = pubsub.PubSubPool(client)


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=my_token,
            prefix="!",
            initial_channels=INIT_CHANNELS,
        )

    @client.event()
    async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
        if event.reward.title == 'Трек':
            link = event.input
            if re.match('^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$', link):
                url = f'{Settings.SERVER_URL}/api/v1/playlist'
                data = {'track': link}
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=data) as resp:
                        await resp.text()
                track = YouTube(link)
                await bot.get_channel('cubinec2012').send(f'@{event.user.name} Трек {track.streams[0].title} успешно добавлен в плейлист!')
            else:
                await bot.get_channel('cubinec2012').send(f'@{event.user.name} только youtube ссылки PixelBob')
        elif event.reward.title == 'Скип':
            pass

    # @commands.command(name='скип')
    # async def skip_track(self, ctx):
    #     await ctx.channel.send('Skipping the current track!')

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
