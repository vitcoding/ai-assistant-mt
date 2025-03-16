from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TokenLayout(BaseModel):
    sub: str
    acc: str
    exp: int
    typ: str


class RefreshTokenInDB(BaseModel):
    id: UUID
    user_id: UUID
    user_role: str
    refresh_token: str
    user_agent: str
    user_device_type: str
    login_time: datetime = Field(..., alias="created_at")

    class Config:
        populate_by_name = True


class RefreshTokenSession(BaseModel):
    login_time: datetime
    user_agent: str
