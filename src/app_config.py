import os

from dotenv import load_dotenv

load_dotenv()

# Database configs dev
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

# # Database configs non-dev
# DB_HOST = os.environ.get("POSTGRES_HOST")
# DB_PORT = os.environ.get("POSTGRES_PORT")
# DB_NAME = os.environ.get("POSTGRES_DB")
# DB_USER = os.environ.get("POSTGRES_USER")
# DB_PASS = os.environ.get("POSTGRES_PASSWORD")

# Database configs for tests dev
DB_HOST_TEST = os.environ.get("DB_HOST_TEST")
DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
DB_PASS_TEST = os.environ.get("DB_PASS_TEST")
DB_PORT_TEST = os.environ.get("DB_PORT_TEST")
DB_USER_TEST = os.environ.get("DB_USER_TEST")

# Auth secrets
SECRET_AUTH = os.environ.get("SECRET_AUTH")

# Mailing configs
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

# Redis configs dev
REDIS_HOST = os.environ.get('REDIS_HOST_DEV')
REDIS_PORT = os.environ.get('REDIS_PORT_DEV')

# # Redis configs non-dev
# REDIS_HOST = os.environ.get('REDIS_HOST')
# REDIS_PORT = os.environ.get('REDIS_PORT')
