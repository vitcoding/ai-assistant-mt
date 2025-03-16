import uuid
from datetime import datetime, timedelta, timezone

from jose import jwt

from core.config import get_auth_data

USER_ID = uuid.uuid4()
USER_DATA = {"sub": str(USER_ID), "acc": "admin"}


def create_access_token(
    type_: str = "access",
    data: dict = USER_DATA,
    expire_seconds: int = 60 * 60,
) -> str:
    """Create a JWT access token."""

    to_encode = data
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


def create_cookies(expired: bool = False) -> dict:
    """Create authorization cookies."""
    if expired:
        access_token = create_access_token(expire_seconds=1)
    else:
        access_token = create_access_token()
    return {"users_access_token": access_token}
