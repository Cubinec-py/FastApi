from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(
    prefix='/pages',
    tags=['Page']
)


@router.get("/base")
def get_base_page(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@router.get("/chat")
def get_chat_page(request: Request):
    return templates.TemplateResponse("chat/chat.html", {"request": request})
