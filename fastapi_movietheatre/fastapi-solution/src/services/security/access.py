import http

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.logger import log
from services.security.token import decode_token


class JWTBearer(HTTPBearer):
    """JWTBearer token class."""

    def __init__(self, auto_error: bool = True) -> None:
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        """Overriding the method of the HTTPBearer parent class."""

        log.debug(f"\nrequest.headers: \n{request.headers}\n")

        credentials: HTTPAuthorizationCredentials = await super().__call__(
            request
        )
        log.debug(f"\ncredentials: \n{credentials}\n")

        if not credentials:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Invalid authorization code.",
            )
        if not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail="Only Bearer token might be accepted",
            )

        decoded_token = self.parse_token(credentials.credentials)
        if not decoded_token:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Invalid or expired token.",
            )
        return decoded_token

    @staticmethod
    def parse_token(jwt_token: str) -> dict | None:
        """Decode token."""
        return decode_token(jwt_token)


security_jwt = JWTBearer()
