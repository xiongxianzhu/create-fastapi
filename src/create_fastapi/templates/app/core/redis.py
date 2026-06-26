"""Redis 异步客户端封装。"""

from __future__ import annotations

from redis.asyncio import Redis


class RedisClient:
    def __init__(self) -> None:
        self._client: Redis | None = None

    async def initialize(self, url: str) -> None:
        self._client = Redis.from_url(url, decode_responses=True)

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> Redis:
        if self._client is None:
            raise RuntimeError("Redis 尚未初始化")
        return self._client


redis_client = RedisClient()
