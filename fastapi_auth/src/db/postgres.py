from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker  # type: ignore

from core.config import settings

Base = declarative_base()

dsn = (
    f"postgresql+asyncpg://{settings.postgres_user}:"
    + f"{settings.postgres_password}@{settings.postgres_host}:"
    + f"{settings.postgres_port}/{settings.postgres_db}"
)
dsn_sync = (
    f"postgresql+psycopg://{settings.postgres_user}:"
    + f"{settings.postgres_password}@{settings.postgres_host}:"
    + f"{settings.postgres_port}/{settings.postgres_db}"
)

engine = create_async_engine(dsn, echo=True, future=True)

async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
sync_engine = create_engine(dsn_sync, echo=False)
sync_session = sessionmaker(sync_engine)


async def get_session() -> AsyncGenerator:
    """Session generator."""

    async with async_session() as session:
        try:
            yield session
        except Exception as err:
            await session.rollback()
            raise err
        finally:
            await session.close()


async def purge_database() -> None:
    """Purge a database function."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
