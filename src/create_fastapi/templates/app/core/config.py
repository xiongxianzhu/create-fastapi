"""基于 pydantic-settings 的类型化配置。"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: str = "development"
    app_name: str = "{{ project_name }}"
    secret_key: str
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/{{ package_name }}"
    )
{% if use_redis %}
    redis_url: str = "redis://localhost:6379/0"
{% endif %}
{% if use_celery %}
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
{% endif %}


@lru_cache
def get_settings() -> Settings:
    return Settings()
