import json
from http import HTTPStatus

import aiohttp
import pytest

from core.config import service_url
from core.conftest import aiohttp_session
from core.logger import log
from tools.token import create_cookies

auth_cookies = create_cookies()
expired_auth_cookies = create_cookies(expired=True)


@pytest.mark.parametrize(
    "auth_cookies, api_return, type_return",
    [
        (
            {},
            HTTPStatus.OK,
            "text/html",
        ),
        (
            expired_auth_cookies,
            HTTPStatus.OK,
            "text/html",
        ),
        (
            auth_cookies,
            HTTPStatus.OK,
            "text/html",
        ),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_add_notification(
    aiohttp_session: aiohttp.ClientSession,
    auth_cookies,
    api_return,
    type_return,
) -> None:
    """Chat api test."""

    url = service_url + "/api/v1/chat_ai/"
    async with aiohttp_session.get(url, cookies=auth_cookies) as response:
        status = response.status
        _content_type = response.content_type
        log.debug(f"\nResponse: \n{response}.\n")

    assert status == api_return
    assert _content_type == type_return
