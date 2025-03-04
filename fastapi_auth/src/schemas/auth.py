from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuthData(BaseModel):
    user_id: UUID
    user_role: str
    expire_time: datetime
