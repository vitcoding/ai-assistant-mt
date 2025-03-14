from abc import ABC, abstractmethod
from typing import Any

from redis.asyncio import Redis

from core.logger import log

CACHE_EXPIRE_IN_SECONDS = 60 * 60 * 24 * 10


class Cache(ABC):
    """An abstract class for work with cache."""

    @abstractmethod
    def get(self, *args, **kwargs): ...

    @abstractmethod
    def set(self, *args, **kwargs): ...


# class CacheService(Cache):
#     """Cache managing service."""

#     async def get(self, client: Redis, key: str) -> Any:
#         """Gets data from cache."""

#         data = await client.get(key)
#         if not data:
#             return None
#         log.info("\nThe data is taken from redis.\n")
#         return data

#     async def set(
#         self,
#         client: Redis,
#         key: str,
#         data: str,
#         expire: int,
#     ) -> None:
#         """Puts data in cache."""

#         await client.set(key, data, expire)
#         log.info("\nThe data is placed in redis.\n")


class CacheService(Cache):
    """Cache managing service."""

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> Any:
        """Gets data from cache."""

        data = await self.redis.get(key)
        if not data:
            return None
        log.info("\nThe data is taken from redis.\n")
        return data

    async def set(
        self, key: str, data: str, expire: int = CACHE_EXPIRE_IN_SECONDS
    ) -> None:
        """Puts data in cache."""

        await self.redis.set(key, data, expire)
        log.info("\nThe data is placed in redis.\n")
