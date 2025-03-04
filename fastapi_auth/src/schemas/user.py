from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserLogin(BaseModel):
    login: str = Field("login")
    password: str = Field("password")


class UserCreate(UserLogin):
    first_name: str = Field("noname")
    last_name: str = Field("noname")
    email: str = Field("no")


class UserInDB(BaseModel):
    id: UUID
    login: str
    password: str
    first_name: str | None
    last_name: str | None
    about: str | None
    birth_date: date | None
    email: str | None
    phone_number: str | None
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserView(BaseModel):
    id: UUID
    login: str
    first_name: str | None
    last_name: str | None
    about: str | None
    birth_date: date | None
    email: str | None
    phone_number: str | None
    role: str | None
    created_at: datetime


class UserAdminView(UserView):
    updated_at: datetime


class UserListAdminView(BaseModel):
    id: UUID
    login: str
    role: str | None
    created_at: datetime


class UserRoleView(BaseModel):
    id: UUID
    login: str
    role: str | None


class AdminCreate(BaseModel):
    login: str = Field("admin")
    password: str = Field("admin")
    first_name: str = Field("admin")
    last_name: str = Field("admin")
    role: str = Field("admin")
