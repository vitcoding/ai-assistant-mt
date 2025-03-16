from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from fastapi.security import APIKeyCookie
from jose import JWTError, jwt
from starlette.requests import Request

from core.config import config


class UpgradeAPIKeyCookie(APIKeyCookie):
    @staticmethod
    def get_current_user(token) -> UUID:
        """
        Get the current user from a JWT token, validating its existence, validity, and expiration.
        """
        try:
            payload = jwt.decode(
                token,
                config.auth.secret_key,
                algorithms=[config.auth.algoritm],
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The token is not valid!",
            )
        expire = payload.get("exp")
        expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
        if (not expire) or (expire_time < datetime.now(timezone.utc)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The token has expired",
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The user ID was not found",
            )

        return UUID(user_id)

    async def __call__(self, request: Request) -> Optional[str]:
        token = await super().__call__(request)
        user_id = self.get_current_user(token)

        return token, user_id
