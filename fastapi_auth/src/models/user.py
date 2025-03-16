import uuid
from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50), default="noname")
    last_name = Column(String(50), default="noname")
    about = Column(String(255), default=None, nullable=True)
    birth_date = Column(Date, default=None, nullable=True)
    email = Column(String(255), default=None, nullable=True)
    phone_number = Column(String(255), default=None, nullable=True)
    role = Column(String(50), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __init__(
        self,
        login: str,
        password: str,
        first_name: str = "noname",
        last_name: str = "noname",
        about: str | None = None,
        birth_date: date | None = None,
        email: str | None = None,
        phone_number: str | None = None,
        role: str = "user",
    ) -> None:
        self.login = login
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.about = about
        self.birth_date = birth_date
        self.email = email
        self.phone_number = phone_number
        self.role = role

    def __repr__(self) -> str:
        return f"<User {self.login}>"
