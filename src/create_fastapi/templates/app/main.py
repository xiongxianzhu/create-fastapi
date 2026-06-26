"""FastAPI 应用入口。"""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
{% if use_redis %}
from redis.asyncio import Redis
{% endif %}

from app.api.v1.admin.router import admin_router
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.db.session import engine
{% if use_redis %}
from app.core.redis import redis_client
{% endif %}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
{% if use_redis %}
    await redis_client.initialize(settings.redis_url)
{% endif %}
    yield
{% if use_redis %}
    await redis_client.close()
{% endif %}
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
    )
    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api/v1")
    app.include_router(admin_router, prefix="/api/admin/v1")
    return app


app = create_app()
