import os
from dotenv import load_dotenv

load_dotenv()


if os.environ.get("SETTINGS") == "Local":
    from src.settings.local.settings import *
elif os.environ.get("SETTINGS") == "Dev":
    from src.settings.dev.settings import *
