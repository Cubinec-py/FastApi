import os

from dotenv import load_dotenv

load_dotenv()

# Database configs
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

# Auth and Manager secrets
SECRET_AUTH = os.environ.get("AUTH")
SECRET_MANAGER = os.environ.get("MANAGER")

# Mailing configs
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
