import os
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from pathlib import Path

load_dotenv()


if os.environ.get("SETTINGS") == "Local":
    from src.settings.local.settings import *
elif os.environ.get("SETTINGS") == "Dev":
    from src.settings.dev.settings import *

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
