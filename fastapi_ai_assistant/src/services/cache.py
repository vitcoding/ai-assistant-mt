from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any

from fastapi import Depends
from redis.asyncio import Redis

from core.logger import log
from db.redis import get_cache_client

CACHE_EXPIRE_IN_SECONDS = 60 * 60 * 24 * 10


class Cache(ABC):
    """An abstract class for work with cache."""

    @abstractmethod
    def get(self, *args, **kwargs): ...

    @abstractmethod
    def set(self, *args, **kwargs): ...


class CacheService(Cache):
    """Cache managing service."""

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> Any:
        """Gets the data from the cache."""

        data = await self.redis.get(key)
        if not data:
            return None
        log.info("\nThe data is taken from redis.\n")
        return data

    async def set(
        self, key: str, data: str, expire: int = CACHE_EXPIRE_IN_SECONDS
    ) -> None:
        """Places the data in the cache.."""

        await self.redis.set(key, data, expire)
        log.info("\nThe data is placed in redis.\n")


@lru_cache()
def get_cache_service(
    redis: Redis = Depends(get_cache_client),
) -> CacheService:
    """Provides CacheService."""
    cache_service = CacheService(redis)
    return CacheService(cache_service)
