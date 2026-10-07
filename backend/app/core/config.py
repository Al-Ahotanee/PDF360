"""
Centralized application configuration.

All environment-dependent values are read here, once, via pydantic-settings.
Nothing else in the codebase should call os.environ directly — import `settings`
from this module instead. This keeps config changes (e.g. swapping storage
providers, rotating secrets) to a single file.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "PDF360"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Security ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Database ---
    DATABASE_URL: str

    # --- Redis / Celery ---
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # --- Storage ---
    STORAGE_PROVIDER: str = "local"  # "local" | "s3"
    LOCAL_STORAGE_PATH: str = "./storage"
    S3_BUCKET_NAME: str | None = None
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None
    S3_REGION: str | None = None
    S3_ENDPOINT_URL: str | None = None

    # Native AWS / Neon environment variable aliases
    AWS_ENDPOINT_URL_S3: str | None = None
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str | None = None

    @property
    def effective_s3_endpoint_url(self) -> str | None:
        return self.S3_ENDPOINT_URL or self.AWS_ENDPOINT_URL_S3

    @property
    def effective_s3_access_key(self) -> str | None:
        return self.S3_ACCESS_KEY or self.AWS_ACCESS_KEY_ID

    @property
    def effective_s3_secret_key(self) -> str | None:
        return self.S3_SECRET_KEY or self.AWS_SECRET_ACCESS_KEY

    @property
    def effective_s3_region(self) -> str | None:
        return self.S3_REGION or self.AWS_REGION

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:3000"

    # --- AI (stubbed) ---
    AI_PROVIDER: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — pydantic-settings reads .env only once per process."""
    return Settings()


settings = get_settings()
