import smtplib
import requests
import redis

from celery import Celery

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
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    data = {'video_url': video_url}
    set_current_track(video_url)
    req = requests.post(f"{Settings.SERVER_URL}/api/v1/playlist/song_add", headers=headers, json=data)
    return print(req.json())


def set_current_track(video_url: str):
    r = redis.Redis.from_url(Settings.REDIS_URL)
    r.set('video_url', video_url)
