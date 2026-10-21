from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PSYCOPG_SCHEME = "postgresql+psycopg://"
PLAIN_POSTGRES_SCHEMES = ("postgresql://", "postgres://")


class Settings(BaseSettings):
    app_name: str = "LedgerKit"
    app_env: Literal["local", "test", "prod"]
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    app_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    app_db_url: PostgresDsn
    app_db_migration_url: PostgresDsn | None = None
    app_db_pool_size: int = 5
    app_db_max_overflow: int = 10
    app_db_connect_timeout_seconds: int = Field(default=5, gt=0)
    app_health_db_timeout_ms: int = Field(default=2000, gt=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Plain postgresql:// URLs (as Neon hands them out) default to psycopg2, which isn't installed.
    @field_validator("app_db_url", "app_db_migration_url", mode="before")
    @classmethod
    def use_psycopg_driver(cls, value: object) -> object:
        if isinstance(value, str):
            for scheme in PLAIN_POSTGRES_SCHEMES:
                if value.startswith(scheme):
                    return PSYCOPG_SCHEME + value.removeprefix(scheme)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
