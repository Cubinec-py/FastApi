import smtplib
from email.message import EmailMessage

from celery import Celery

from settings.settings import *

celery = Celery('tasks', broker=Settings.REDIS_URL)


def get_user_email_template(username: str):
    email = EmailMessage()
    email['Subject'] = 'Натрейдил Отчет Дашборд'
    email['From'] = Settings.SMTP_USER
    email['To'] = Settings.SMTP_USER

    email.set_content(
        '<div>'
        f'<h1 style="color: red;">Здравствуйте, {username}, а вот и ваш отчет. Зацените 😊</h1>'
        '<img src="https://static.vecteezy.com/system/resources/previews/008/295/031/original/custom-relationship'
        '-management-dashboard-ui-design-template-suitable-designing-application-for-android-and-ios-clean-style-app'
        '-mobile-free-vector.jpg" width="600">'
        '</div>',
        subtype='html'
    )
    return email


@celery.task
def send_mail(username: str):
    email = get_user_email_template(username)
    with smtplib.SMTP_SSL(Settings.SMTP_HOST, Settings.SMTP_PORT) as server:
        server.login(Settings.SMTP_USER, Settings.SMTP_PASSWORD)
        server.send_message(email)
