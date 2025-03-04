from functools import lru_cache
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from db.redis import get_redis
from models.token import RefreshToken
from models.user import User
from schemas.token import RefreshTokenInDB
from schemas.user import UserInDB
from services.abstracts import AbstractService
from services.cache import CacheService
from services.database import DBService

from .pagination import PaginationParams


class UsersService(AbstractService):
    """Users managing service."""

    async def get_user_by_id(self, id: UUID) -> UserInDB:
        """Get user by id."""

        user_db = await self.db_service.get_item_by_attribute(User, "id", id)
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The user not found.",
            )
        user = UserInDB(**jsonable_encoder(user_db))
        return user

    async def get_user_by_login(self, login: str):
        """Get user by login."""

        user_db = await self.db_service.get_item_by_attribute(
            User, "login", login
        )
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The user not found.",
            )
        user = UserInDB(**jsonable_encoder(user_db))
        return user

    async def get_users(
        self,
        sort_field: str,
        pagination: PaginationParams,
    ) -> list[UserInDB]:
        """Get a paginated list of the users."""

        users_db = await self.db_service.get_items(
            User, sort_field, pagination
        )
        if not users_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Users not found"
            )

        users = [UserInDB(**jsonable_encoder(user)) for user in users_db]
        return users

    async def get_user_sessions(
        self,
        user_id: UUID,
        sort_field: str,
        pagination: PaginationParams,
    ) -> list:
        """Get a paginated list of the user's sessions."""

        refresh_tokens_db = await self.db_service.get_items_with_condition(
            RefreshToken, "user_id", user_id, sort_field, pagination
        )
        if not refresh_tokens_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sessions not found",
            )

        refresh_tokens = [
            RefreshTokenInDB(**jsonable_encoder(token))
            for token in refresh_tokens_db
        ]
        return refresh_tokens


@lru_cache()
def get_users_service(
    db: AsyncSession = Depends(get_session),
    cache: Redis = Depends(get_redis),
) -> UsersService:
    """UsersService provider."""
    db_service = DBService(db)
    cache_service = CacheService(cache)
    return UsersService(db_service, cache_service)
