from functools import lru_cache
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import log
from db.postgres import get_session
from db.redis import get_redis
from models.token import RefreshToken
from models.user import User
from schemas.token import TokenLayout
from schemas.user import UserCreate, UserInDB
from services.abstracts import AbstractService
from services.cache import CacheService
from services.database import DBService
from services.token import get_token_service
from services.tools.device_type import get_device_type


class AuthPasswordService:
    """Password managing service."""

    _context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """Get the password's hash."""
        return cls._context.hash(password)

    @classmethod
    def verify_password(cls, password: str, hashed_password: str) -> bool:
        """Verify the password's hashes."""
        return cls._context.verify(password, hashed_password)


class AuthService(AbstractService):

    async def create_admin(self, user_dict: dict) -> UserInDB:
        """Create an admin."""

        login = user_dict["login"]
        user_login_check = await self.db_service.get_item_by_attribute(
            User, "login", login
        )
        if user_login_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The login '{login}' is already in use.",
            )
        hashed_password = AuthPasswordService.get_password_hash(
            user_dict["password"]
        )
        user_dict["password"] = hashed_password
        user_db = User(**user_dict)
        await self.db_service.put_item(User, user_db)
        return UserInDB(**jsonable_encoder(user_db))

    async def create_user(
        self,
        user_create: UserCreate,
        user_agent: str,
    ) -> tuple[UserInDB, str]:
        """Creata a user."""

        user_in_db = await self.db_service.get_item_by_attribute(
            User, "login", user_create.login
        )
        if user_in_db:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"The login '{user_create.login}' is already in use.",
            )

        user_dict = user_create.model_dump()
        hashed_password = AuthPasswordService.get_password_hash(
            user_create.password
        )
        user_dict["password"] = hashed_password
        log.debug("\nCreate user: \n%S\n", user_dict)
        user_db = User(**user_dict)
        log.info("\nuser_db: \n%s\n", user_db)
        await self.db_service.put_item(User, user_db)

        access_token, _ = await self.get_tokens(
            user_db.id, user_db.role, user_agent
        )
        user = UserInDB(**jsonable_encoder(user_db))
        return user, access_token

    async def change_user_auth_data(
        self, user_id: UUID, new_login: str | None, new_password: str | None
    ):
        """Change the user's login or / and password."""

        if new_login is None and new_password is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nothing to change.",
            )

        user_db = await self.db_service.get_item_by_attribute(
            User, "id", user_id
        )
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The user not found.",
            )

        if new_login:
            user_login_check = await self.db_service.get_item_by_attribute(
                User, "login", new_login
            )
            if user_login_check:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"The login '{new_login}' is already in use.",
                )

        if new_password:
            verified_password = AuthPasswordService.verify_password(
                password=new_password, hashed_password=user_db.password
            )

        if (
            (new_login == user_db.login and new_password is None)
            or (new_login is None and verified_password)
            or (new_login == user_db.login and verified_password)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The login or password must be different from "
                + "the old ones.",
            )

        if new_login:
            user_db.login = new_login

        if new_password:
            new_hashed_password = AuthPasswordService.get_password_hash(
                new_password
            )
            user_db.password = new_hashed_password
        await self.db_service.update_item(User, user_db)

        user = UserInDB(**jsonable_encoder(user_db))
        return user

    async def delete_user_auth_data(self, user_id: UUID) -> None:
        """Delete the user's auth data."""

        user_db = await self.db_service.get_item_by_attribute(
            User, "id", user_id
        )
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The user not found.",
            )

        await self.db_service.delete_item(User, user_db)

    async def authenticate_user(
        self,
        login: str,
        password: str,
        user_agent: str,
    ) -> tuple:
        """Authenticate a user."""

        user_db = await self.db_service.get_item_by_attribute(
            User, "login", login
        )
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The user not found.",
            )

        user_db = UserInDB(**jsonable_encoder(user_db))
        log.info("\nuser: \n%s\n", user_db)
        if (
            not user_db
            or AuthPasswordService.verify_password(
                password=password, hashed_password=user_db.password
            )
            is False
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login or password.",
            )

        access_token, refresh_token = await self.get_tokens(
            user_db.id, user_db.role, user_agent
        )
        return access_token, refresh_token

    async def refresh_token(
        self,
        access_token: str,
        user_agent: str,
    ) -> tuple:
        """Refresh access and refresh tokens."""

        token_service = get_token_service()

        token_data_dict = token_service.check_token(access_token)
        if token_data_dict is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        token_data = TokenLayout(**token_data_dict)
        user_id = token_data.sub
        user_role = token_data.acc
        access_token, refresh_token = await self.get_tokens(
            user_id, user_role, user_agent
        )
        return access_token, refresh_token

    async def get_tokens(
        self, user_id: UUID | str, user_role: str, user_agent: str
    ) -> tuple:
        """Create access and refresh tokens."""

        token_service = get_token_service()

        token_data_dict = {"sub": str(user_id), "acc": str(user_role)}
        access_token, expire_seconds = token_service.create_access_token(
            token_data_dict
        )
        key = f"access token: user_id: {str(user_id)}"
        await self.cache_service.set(key, access_token, expire_seconds)

        refresh_token, _ = token_service.create_refresh_token(token_data_dict)
        user_device_type = get_device_type(user_agent)
        refresh_token_dict = {
            "user_id": user_id,
            "user_role": user_role,
            "refresh_token": refresh_token,
            "user_agent": user_agent,
            "user_device_type": user_device_type,
        }
        refresh_token_db = RefreshToken(**refresh_token_dict)
        await self.db_service.put_item(RefreshToken, refresh_token_db)

        return access_token, refresh_token

    async def get_last_refresh_token(self, user_id: UUID) -> dict | None:
        last_refresh_token_db = await self.db_service.get_last_item(
            RefreshToken, "user_id", user_id
        )
        return last_refresh_token_db

    async def change_user_role(self, user_id: UUID, new_role: str):
        """Change the user's role."""

        user_db = await self.db_service.get_item_by_attribute(
            User, "id", user_id
        )
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The user not found.",
            )

        if new_role:
            user_db.role = new_role

        await self.db_service.update_item(User, user_db)
        user = UserInDB(**jsonable_encoder(user_db))
        return user


@lru_cache()
def get_auth_service(
    db: AsyncSession = Depends(get_session),
    cache: Redis = Depends(get_redis),
) -> AuthService:
    """AuthService provider."""
    db_service = DBService(db)
    cache_service = CacheService(cache)
    return AuthService(db_service, cache_service)
