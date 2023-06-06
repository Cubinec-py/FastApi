from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.middleware.cors import CORSMiddleware

from redis import asyncio as aioredis

from src.auth.base_config import auth_backend, fastapi_users
from src.auth.schemas import UserRead, UserCreate, UserUpdate
from src.operations.router import router as router_operation
from src.tasks.router import router as router_task
from src.chat.router import router as router_chat
from src.pages.router import router as router_page
from src.playlist.router import router as router_playlist

from src.settings.settings import Settings

app = FastAPI(
    debug=Settings.DEBUG,
    version="0.0.1",
    default_response_class=ORJSONResponse,
    title="FastAPI App"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Settings.CORS_ALLOW_ORIGINS,
    allow_credentials=Settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=Settings.CORS_ALLOW_METHODS,
    allow_headers=Settings.CORS_ALLOW_HEADERS,
)


@app.on_event(event_type="startup")
async def startup():
    redis = aioredis.from_url(
        Settings.REDIS_URL, encoding="utf8", decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


API_PREFIX = "/api/v1"

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix=API_PREFIX,
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix=API_PREFIX,
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix=f"{API_PREFIX}/users",
    tags=["Users"],
)

app.include_router(router=router_operation, prefix=API_PREFIX)
app.include_router(router=router_task, prefix=API_PREFIX)
app.include_router(router=router_playlist, prefix=API_PREFIX)
app.include_router(router=router_chat)
app.include_router(router=router_page)
