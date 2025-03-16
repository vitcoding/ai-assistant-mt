from typing import Any
from uuid import UUID

from fastapi import Depends
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import log
from db.postgres import get_session

from .pagination import PaginationParams


class DBService:
    """Database managing service."""

    def __init__(self, db_service: AsyncSession = Depends(get_session)):
        self.db_service = db_service

    async def get_item_by_attribute(
        self, model: Any, attribute: str, value: Any
    ) -> Any | None:
        """Get an item by attribute from the database."""

        stmt = select(model).where(
            model.__getattribute__(model, attribute) == value
        )
        item: Any | None = await self.db_service.scalar(stmt)
        log.debug("\nitem by id: \n%s.\n", item)
        if not item:
            return None
        log.info("\nGetting data from the db.\n")
        return item

    async def get_items(
        self,
        model: Any,
        sort_field: str,
        pagination: PaginationParams,
    ) -> list[Any] | None:
        """Get a list of items from the database."""

        if sort_field is not None and len(sort_field) > 1:
            order = (asc, desc)[sort_field.startswith("-")]
            if sort_field.startswith(("-", "+")):
                sort_field = sort_field[1:]
        offset = (pagination.page_number - 1) * pagination.page_size
        stmt = (
            select(model)
            .order_by(order(getattr(model, sort_field)))
            .offset(offset)
            .limit(pagination.page_size)
        )
        data = await self.db_service.scalars(stmt)
        return data

    async def get_items_with_condition(
        self,
        model: Any,
        attribute: str,
        value: Any,
        sort_field: str,
        pagination: PaginationParams,
    ) -> list[Any] | None:
        """Get a list of items from the database with the condition."""

        if sort_field is not None and len(sort_field) > 1:
            order = (asc, desc)[sort_field.startswith("-")]
            if sort_field.startswith(("-", "+")):
                sort_field = sort_field[1:]
        offset = (pagination.page_number - 1) * pagination.page_size
        stmt = (
            select(model)
            .where(model.__getattribute__(model, attribute) == value)
            .order_by(order(getattr(model, sort_field)))
            .offset(offset)
            .limit(pagination.page_size)
        )
        data = await self.db_service.scalars(stmt)
        return data

    async def get_last_item(
        self,
        model: Any,
        attribute: str,
        value: Any,
        sort_field: str = "created_at",
    ) -> Any | None:
        """Get the last item by attribute from the database."""

        stmt = (
            select(model)
            .where(model.__getattribute__(model, attribute) == value)
            .order_by(desc(getattr(model, sort_field)))
            .limit(1)
        )
        data: Any | None = await self.db_service.scalar(stmt)
        if not data:
            return None
        return data

    async def put_item(self, model: Any, item: Any):
        """Put an item to the database."""

        self.db_service.add(item)
        await self.db_service.commit()
        await self.db_service.refresh(item)

    async def update_item(self, model: Any, item: Any):
        """Update the item in the database."""

        await self.db_service.commit()
        await self.db_service.refresh(item)

    async def delete_item(self, model: Any, item: Any):
        """Delete the item from the database."""

        await self.db_service.delete(item)
        await self.db_service.commit()
