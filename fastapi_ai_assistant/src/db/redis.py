from typing import AsyncGenerator

from redis.asyncio import Redis

from core.config import config

redis: Redis | None = None


async def get_cache_client() -> Redis | None:
    return redis


# async def get_client() -> AsyncGenerator:
#     async with Redis(host=config.cache.host, port=config.cache.port) as client:
#         yield client
