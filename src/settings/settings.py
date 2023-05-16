import os
from dotenv import load_dotenv

load_dotenv()


if os.environ.get("SETTINGS") == "Local":
    from .local.settings import *
elif os.environ.get("SETTINGS") == "Dev":
    from .dev.settings import *
