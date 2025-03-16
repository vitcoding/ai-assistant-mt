from redis.asyncio import Redis

redis: Redis | None = None


async def get_cache_client() -> Redis | None:
    return redis
