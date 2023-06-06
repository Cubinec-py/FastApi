"""Config file for gunicorn application."""
# from src.settings.loggers import LOGGING_CONFIG
from src.settings.settings import Settings

bind = f"{Settings.HOST}:{Settings.PORT}"
workers = Settings.WORKERS_COUNT
log_level = Settings.LOG_LEVEL
worker_class = "uvicorn.workers.UvicornWorker"
threads = 1  # default
reload = True
reload_engine = "auto"
max_requests = 100  # default 0
max_requests_jitter = 3  # default 0
# logconfig_dict = LOGGING_CONFIG
errorlog = '-'
accesslog = '-'
