from jose import jwt

from core.config import settings
from core.logger import log


def decode_token(token: str) -> dict | None:
    """Decode JWT token."""
    try:
        jwt_data = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        log.info(f"\njwt_data: \n{jwt_data}\n")
        return jwt_data
    except Exception:
        return None
