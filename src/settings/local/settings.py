import functools
import logging

from pydantic import BaseSettings, Extra, Field

origins = [
    "http://127.0.0.1:8000",
]


class Settings(BaseSettings):
    # Back-end settings
    DEBUG: bool = Field(default=True)
    SHOW_SETTINGS: bool = Field(default=True)
    HOST: str = Field()
    PORT: str = Field()
    SERVER_URL: str = Field()
    WS_URL: str = Field()
    WORKERS_COUNT: int = Field(default=1)
    DATETIME_FORMAT: str = Field(default="%Y-%m-%d %H:%M:%S")
    TRUSTED_HOSTS: list[str] = Field(default=["*"])
    # CORS settings
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    CORS_ALLOW_HEADERS: list[str] = Field(
        default=[
            "Content-Type",
            "Set-Cookie",
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Origin",
            "Authorization",
        ]
    )
    CORS_ALLOW_METHODS: list[str] = Field(
        default=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"]
    )
    CORS_ALLOW_ORIGINS: list[str] = Field(default=origins)
    # JWT tokens managements settings
    TOKENS_ACCESS_LIFETIME_SECONDS: int = Field(default=3600)  # 1 HOUR
    TOKENS_REFRESH_LIFETIME_SECONDS: int = Field(default=86400)  # 1 DAY
    TOKENS_SECRET_KEY: str = Field(default="SECRET")
    # Logging settings
    LOG_LEVEL: int = Field(default=logging.DEBUG)
    LOG_USE_COLORS: bool = Field(default=True)
    # Database settings
    DATABASE_URL: str = Field()
    # Redis settings
    REDIS_URL: str = Field()
    # Google mail SMTP settings
    SMTP_HOST: str = Field()
    SMTP_PORT: int = Field()
    SMTP_USER: str = Field()
    SMTP_PASSWORD: str = Field()

    class Config(BaseSettings.Config):
        extra = Extra.ignore
        env_file = ".env.local"
        env_file_encoding = "UTF-8"
        env_nested_delimiter = "__"


@functools.lru_cache()
def get_settings() -> Settings:
    return Settings()


Settings: Settings = get_settings()
