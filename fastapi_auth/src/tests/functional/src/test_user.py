from http import HTTPStatus

import aiohttp
import pytest

from core.config import service_url
from core.conftest import aiohttp_session
from core.logger import log
from utils.cookie import TokensUtils, get_user_cookies

LOGIN = "user101"


@pytest.mark.parametrize(
    "user, api_return",
    [
        (
            {
                "login": LOGIN,
                "password": "pass123",
            },
            HTTPStatus.CREATED,
        ),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_auth(
    aiohttp_session: aiohttp.ClientSession, user, api_return
) -> None:
    """Create user for the second test."""

    url = service_url + "/api/v1/auth/signup"
    async with aiohttp_session.post(url, json=user) as response:
        status = response.status
        log.debug(f"\nResponse: \n{response}.\n")
        log.debug(f"\nCookies: \n{response.cookies}.\n")
        TokensUtils.set_token(str(response.cookies))

    assert status == api_return


@pytest.mark.parametrize(
    "case_num, user_data, api_return",
    [
        (1, {"new_login": "login", "new_password": "password"}, HTTPStatus.OK),
        (
            2,
            {"new_login": "login", "new_password": "password"},
            HTTPStatus.UNAUTHORIZED,
        ),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_user(
    aiohttp_session: aiohttp.ClientSession, case_num, user_data, api_return
) -> None:
    """Get user info test."""

    match case_num:
        case 1:
            user_cookies = get_user_cookies()
            log.debug(f"\nuser_coockies: \n{user_cookies}\n")
        case 2:
            user_cookies = get_user_cookies(wrong=True)
            log.debug(f"\nuser_coockies: \n{user_cookies}\n")

    url = service_url + "/api/v1/user/"
    async with aiohttp_session.get(url, cookies=user_cookies) as response:
        status = response.status
        log.debug(f"\nResponse: \n{response}.\n")

    assert status == api_return
