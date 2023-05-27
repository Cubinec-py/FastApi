import smtplib
import requests

from celery import Celery

from src.twitch.utils import get_track_url
from src.tasks.utils import get_user_email_template
from src.settings.settings import Settings

celery = Celery("tasks", broker=Settings.REDIS_URL, backend=Settings.REDIS_URL)


@celery.task
def send_mail(username: str):
    email = get_user_email_template(username)
    with smtplib.SMTP_SSL(Settings.SMTP_HOST, Settings.SMTP_PORT) as server:
        server.login(Settings.SMTP_USER, Settings.SMTP_PASSWORD)
        server.send_message(email)


@celery.task
def skip_track(video_url: str):
    data = {"url": video_url}
    requests.post(f"{Settings.SERVER_URL}/api/v1/playlist/song_add", params=data)


async def next_track():
    data = await get_track_url()
    skip_track.apply_async(data.track)
