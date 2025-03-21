import base64
import json
from datetime import datetime, timedelta, timezone
from functools import lru_cache

from fastapi import HTTPException, Request, Response, status
from jose import jwt
from jose.exceptions import ExpiredSignatureError

from core.config import get_auth_data
from core.logger import log
from schemas.auth import AuthData

# in seconds
ACCESS_EXPIRE = 1 * 60 * 60 * 24  # 30 * 60
REFRESH_EXPIRE = 10 * 60 * 60 * 24  # 10 * 60 * 60 * 24


class TokenService:
    """Tokens managing service."""

    @staticmethod
    def create_token(
        type_: str, data: dict, expire_seconds: int | float
    ) -> str:
        """Create a JWT token."""

        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(seconds=expire_seconds)
        to_encode.update({"exp": expire})
        to_encode.update({"typ": type_})
        auth_data = get_auth_data()
        encoded_jwt = jwt.encode(
            to_encode,
            key=auth_data["secret_key"],
            algorithm=auth_data["algorithm"],
        )
        return encoded_jwt

    def create_access_token(
        self, data: dict, expire_seconds: int = ACCESS_EXPIRE
    ) -> tuple[str, int]:
        """Create an access JWT token."""

        encoded_jwt = self.__class__.create_token(
            "access", data, expire_seconds
        )
        return encoded_jwt, expire_seconds

    def create_refresh_token(
        self, data: dict, expire_seconds: int = REFRESH_EXPIRE
    ) -> tuple[str, int]:
        """Create a refresh JWT token."""

        encoded_jwt = self.__class__.create_token(
            "refresh", data, expire_seconds
        )
        return encoded_jwt, expire_seconds

    def decode_token(self, token: str) -> dict:
        """Decode a JWT token."""

        auth_data = get_auth_data()
        decoded_jwt = jwt.decode(
            token,
            key=auth_data["secret_key"],
            algorithms=[auth_data["algorithm"]],
        )
        return decoded_jwt

    def check_token(self, token: str, access_data: bool = False) -> tuple:
        """Validate the JWT token."""

        flag = True
        try:
            token_data = self.decode_token(token)
        except ExpiredSignatureError:
            try:
                parts = token.split(".")
                payload = base64.urlsafe_b64decode(
                    parts[1] + "=" * (-len(parts[1]) % 4)
                ).decode("utf-8")
            except Exception as err:
                raise ValueError("Failed to decode JWT payload") from err
            token_data = json.loads(payload)
            flag = False
        except Exception as err:
            log.error("\nError '%s': \n%s\n", type(err), err)
            return (None, None)

        expire = token_data.get("exp", 0)

        expire_time = datetime.fromtimestamp(expire, tz=timezone.utc)
        log.debug(
            "\ntoken layout: \n%s\nexpire time: %s\n",
            token_data,
            expire_time,
        )

        if access_data:
            auth_data_dict: dict = {
                "user_id": token_data["sub"],
                "user_role": token_data["acc"],
                "expire_time": expire_time,
            }
            return (flag, auth_data_dict)

        return (flag, token_data)

    def get_access_data(self, request: Request) -> str:
        """Get access data from the cookies."""

        access_token = request.cookies.get("users_access_token")
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token.",
            )
        return access_token

    def set_access_data(
        self,
        response: Response,
        access_token: str,
    ) -> None:
        """Set the access data in cookies."""
        response.set_cookie(
            key="users_access_token", value=access_token, httponly=True
        )


@lru_cache()
def get_token_service():
    """TokenService provider."""
    return TokenService()
