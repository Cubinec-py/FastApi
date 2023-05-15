from fastapi import FastAPI, Depends
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.middleware.cors import CORSMiddleware

from redis import asyncio as aioredis

from auth.base_config import auth_backend, fastapi_users, current_active_user
from auth.models import User
from auth.schemas import UserRead, UserCreate, UserUpdate
from operations.router import router as router_operation
from tasks.router import router as router_task
from chat.router import router as router_chat
from pages.router import router as router_page

from settings.settings import Settings

app = FastAPI(
    title="Trading App"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Settings.CORS_ALLOW_ORIGINS,
    allow_credentials=Settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=Settings.CORS_ALLOW_METHODS,
    allow_headers=Settings.CORS_ALLOW_HEADERS,
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/api/auth/jwt",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/api/users",
    tags=["Users"],
)


@app.get("/api/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.username}"}

app.include_router(router_operation)
app.include_router(router_task)
app.include_router(router_chat)
app.include_router(router_page)


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(
        Settings.REDIS_URL,
        encoding="utf8",
        decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
