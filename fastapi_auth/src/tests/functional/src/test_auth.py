from http import HTTPStatus

import aiohttp
import pytest

from core.config import service_url
from core.conftest import aiohttp_session
from core.logger import log
from utils.cookie import TokensUtils, get_user_cookies

LOGIN = "user11"


@pytest.mark.parametrize(
    "user, api_return",
    [
        (
            {
                "login": LOGIN,
                "password": "pass123",
                "first_name": "John",
                "last_name": "Doe",
            },
            HTTPStatus.CREATED,
        ),
        (
            {
                "login": LOGIN,
                "password": "pass123",
                "first_name": "John",
                "last_name": "Doe",
            },
            HTTPStatus.CONFLICT,
        ),
        (
            {
                "login": "user21",
                "password": "secret456",
                "first_name": "Jane",
                "last_name": "Smith",
            },
            HTTPStatus.CREATED,
        ),
        (
            {
                "login": "admin1",
                "password": "root1234",
                "first_name": "System",
                "last_name": "Administrator",
            },
            HTTPStatus.CREATED,
        ),
        (
            {
                "login": "manager1",
                "password": "boss123",
                "first_name": "Mike",
                "last_name": "Manager",
            },
            HTTPStatus.CREATED,
        ),
        (
            {"login": 1, "password": 1, "first_name": 1, "last_name": 1},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_auth(
    aiohttp_session: aiohttp.ClientSession, user, api_return
) -> None:
    """User signup test."""

    url = service_url + "/api/v1/auth/signup"
    async with aiohttp_session.post(url, json=user) as response:
        status = response.status
        log.debug(f"\nResponse: \n{response}.\n")
        log.debug(f"\nCookies: \n{response.cookies}.\n")
        TokensUtils.set_token(str(response.cookies))

    assert status == api_return


@pytest.mark.parametrize(
    "user_access, api_return",
    [
        ({"login": LOGIN, "password": "pass123"}, HTTPStatus.OK),
        (
            {"login": LOGIN + "None", "password": "pass123"},
            HTTPStatus.NOT_FOUND,
        ),
        ({"login": "user21", "password": "secret456"}, HTTPStatus.OK),
        (
            {"login": "user21", "password": "secret4256"},
            HTTPStatus.UNAUTHORIZED,
        ),
        ({"login": "admin1", "password": "root1234"}, HTTPStatus.OK),
        (
            {"login": "admin101", "password": "root123433"},
            HTTPStatus.NOT_FOUND,
        ),
        ({"login": "manager1", "password": "boss123"}, HTTPStatus.OK),
        ({"login": "manager1", "password": "123123"}, HTTPStatus.UNAUTHORIZED),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_login(
    aiohttp_session: aiohttp.ClientSession, user_access, api_return
) -> None:
    """User login test."""

    url = service_url + "/api/v1/auth/login"
    async with aiohttp_session.post(url, json=user_access) as response:
        status = response.status

    assert status == api_return


@pytest.mark.parametrize(
    "case_num, api_return",
    [
        (1, HTTPStatus.OK),
        (2, HTTPStatus.UNAUTHORIZED),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_token_refresh(
    aiohttp_session: aiohttp.ClientSession, case_num, api_return
) -> None:
    """Token refresh test."""

    match case_num:
        case 1:
            user_cookies = get_user_cookies()
        case 2:
            user_cookies = get_user_cookies(wrong=True)

    url = service_url + "/api/v1/auth/token"
    async with aiohttp_session.post(url, cookies=user_cookies) as response:
        status = response.status
        log.debug(f"\nResponse: \n{response}.\n")

    assert status == api_return


@pytest.mark.parametrize(
    "case_num, api_return",
    [
        (1, HTTPStatus.OK),
        (2, HTTPStatus.UNAUTHORIZED),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_logout(
    aiohttp_session: aiohttp.ClientSession, case_num, api_return
) -> None:
    """User logout test."""

    match case_num:
        case 1:
            user_cookies = get_user_cookies()
        case 2:
            user_cookies = get_user_cookies(wrong=True)

    url = service_url + "/api/v1/auth/logout"
    async with aiohttp_session.post(url, cookies=user_cookies) as response:
        status = response.status

    assert status == api_return
