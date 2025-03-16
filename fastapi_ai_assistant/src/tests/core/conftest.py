import asyncio
from typing import AsyncGenerator, Generator

import aiohttp
import pytest_asyncio


@pytest_asyncio.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Async loop fixture."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name="aiohttp_session", scope="session")
async def aiohttp_session() -> AsyncGenerator:
    """API connection fixture."""
    async with aiohttp.ClientSession() as session:
        yield session
