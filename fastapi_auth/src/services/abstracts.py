import json
from abc import ABC, abstractmethod
from typing import Any

from core.logger import log
from services.cache import CacheService
from services.database import DBService


class AbstractService(ABC):
    """An abstract base class for services."""

    def __init__(
        self,
        db_service: DBService,
        cache_service: CacheService,
    ) -> None:
        self.db_service = db_service
        self.cache_service = cache_service

    async def get_from_cache(
        self, key: str, model: Any, is_list: bool = False
    ) -> Any:
        """Get data from cache."""

        data = await self.cache_service.get(key)
        if not data:
            return None

        if is_list:
            collection = [model(**row) for row in json.loads(data.decode())]
            return collection
        return model.parse_raw(data)

    async def put_to_cache(self, key: str, data: list, model: Any) -> None:
        """Put data in cache."""

        if isinstance(data, list):
            serialized_data = json.dumps(
                [dict(model(**dict(item))) for item in data]
            )
        else:
            serialized_data = data.json()

        await self.cache_service.set(key, serialized_data)
