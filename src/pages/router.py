from fastapi import APIRouter, Request

from src.settings.settings import Settings, templates

router = APIRouter(prefix="/pages", tags=["Page"])


@router.get("/base")
def get_base_page(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@router.get("/chat")
def get_chat_page(request: Request):
    return templates.TemplateResponse(
        "chat/chat.html",
        {
            "request": request,
            "SERVER_URL": Settings.SERVER_URL,
            "WS_URL": Settings.WS_URL,
        },
    )
