import uuid
from uuid import UUID

from pydantic import BaseModel


class RoleCreate(BaseModel):
    name: str
    description: str | None


class RoleUpdate(BaseModel):
    name: str | None
    description: str | None


class RoleInDB(BaseModel):
    id: UUID = uuid.uuid4()
    name: str
    description: str | None

    class Config:
        from_attributes = True