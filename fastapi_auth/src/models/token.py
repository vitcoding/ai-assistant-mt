import uuid
from datetime import datetime

from fastapi import Depends
from sqlalchemy import Column, DateTime, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import Base, get_session


def create_partition(
    target: str, connection: AsyncSession = Depends(get_session), **kwargs
) -> None:
    """Creating partition by refresh_tokens."""

    connection.execute(
        text(
            f"""CREATE TABLE IF NOT EXISTS "{target}_desktop" PARTITION """
            f"""OF "{target}" FOR VALUES IN ('desktop')"""
        )
    )
    connection.execute(
        text(
            f"""CREATE TABLE IF NOT EXISTS "{target}_mobile" PARTITION """
            f"""OF "{target}" FOR VALUES IN ('mobile')"""
        )
    )
    connection.execute(
        text(
            f"""CREATE TABLE IF NOT EXISTS "{target}_other" PARTITION """
            f"""OF "{target}" FOR VALUES IN ('other')"""
        )
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        UniqueConstraint("id", "user_device_type"),
        {
            "postgresql_partition_by": "LIST (user_device_type)",
            "listeners": [("after_create", create_partition)],
        },
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(UUID(as_uuid=True), nullable=False)
    user_role = Column(String(50))
    refresh_token = Column(String(255))
    user_agent = Column(String(255))
    user_device_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(
        self,
        user_id: str,
        user_role: str,
        refresh_token: str,
        user_agent: str,
        user_device_type: str,
    ) -> None:
        self.user_id = user_id
        self.user_role = user_role
        self.refresh_token = refresh_token
        self.user_agent = user_agent
        self.user_device_type = user_device_type

    def __repr__(self) -> str:
        return f"<User's {self.user_id} refresh token>"
