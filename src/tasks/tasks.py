import smtplib
import requests
import datetime

from email.message import EmailMessage

from celery import Celery
from sqlalchemy import select, delete

from src.database import async_session_maker
from src.playlist.models import Playlist
from src.settings.settings import Settings

celery = Celery("tasks", broker=Settings.REDIS_URL, backend=Settings.REDIS_URL)


def get_user_email_template(username: str):
    email = EmailMessage()
    email["Subject"] = "Натрейдил Отчет Дашборд"
    email["From"] = Settings.SMTP_USER
    email["To"] = Settings.SMTP_USER

    email.set_content(
        "<div>"
        f'<h1 style="color: red;">Здравствуйте, {username}, а вот и ваш отчет. Зацените 😊</h1>'
        '<img src="https://static.vecteezy.com/system/resources/previews/008/295/031/original/custom-relationship'
        "-management-dashboard-ui-design-template-suitable-designing-application-for-android-and-ios-clean-style-app"
        '-mobile-free-vector.jpg" width="600">'
        "</div>",
        subtype="html",
    )
    return email


@celery.task
def send_mail(username: str):
    email = get_user_email_template(username)
    with smtplib.SMTP_SSL(Settings.SMTP_HOST, Settings.SMTP_PORT) as server:
        server.login(Settings.SMTP_USER, Settings.SMTP_PASSWORD)
        server.send_message(email)


@celery.task
def skip_track(video_url: str, length: int):
    if length > 300:
        timer = datetime.datetime.now() + datetime.timedelta(seconds=200)
        skip_track_timer(timer)
    data = {"url": video_url}
    requests.post(f"{Settings.SERVER_URL}/api/v1/playlist/song_add", params=data)


async def skip_track_timer(timer: datetime.datetime):
    data = await get_track_url()
    skip_track.apply_async((data.track, data.length), eta=timer)


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
