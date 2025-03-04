from typing import Any

from redis.asyncio import Redis

from core.logger import log

CACHE_EXPIRE_IN_SECONDS = 60 * 5


class CacheService:
    """Cache managing service."""

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> Any:
        """Get data from cache."""

        data = await self.redis.get(key)
        if not data:
            return None
        log.info("\nGetting data from redis.\n")
        return data

    async def set(
        self, key: str, data: str, expire: int = CACHE_EXPIRE_IN_SECONDS
    ) -> None:
        """Put data in cache."""

        await self.redis.set(key, data, expire)
        log.info("\nThe data is placed in redis.\n")
