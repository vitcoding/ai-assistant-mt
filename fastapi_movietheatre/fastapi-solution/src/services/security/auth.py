from httpx import AsyncClient, HTTPError

from core.config import settings
from core.logger import log


class NoTokenException(Exception):
    pass


async def login_access_token(login: str, password: str) -> str:
    """Get an access token from the auth service."""

    async with AsyncClient() as client:
        try:
            urn = "/api/v1/auth/login"
            uri = settings.auth_url + urn

            request_data = {"login": login, "password": password}

            response = await client.post(uri, json=request_data)
            log.info(f"\nresponse status code: {response.status_code}\n")

            if response.status_code == 200:
                users_access_token = response.cookies.get("users_access_token")
                if users_access_token is None:
                    raise NoTokenException
                log.info(f"\ncookies: {users_access_token}\n")
                bearer_token_dict = {
                    "access_token": users_access_token,
                    "token_type": "bearer",
                }
                return bearer_token_dict
            else:
                auth_response = {
                    "error": "Request failed with status code "
                    + f"{response.status_code}"
                }
                return auth_response

        except Exception as err:
            log.error(f"An error '{type(err)}' "
                      f"occurred while requesting data: {err}")
            message = {
                "message": "Unfortunately, authorization is currently " 
                + "unavailable. In the meantime, you can view the list of "
                + "films with a short description."
                }
            return message


async def refresh_access_token(access_token: str) -> str:
    """Get a new access token from the auth service."""

    async with AsyncClient() as client:
        try:
            urn = "/api/v1/auth/token"
            uri = settings.auth_url + urn

            token_cookie = {"users_access_token": access_token}
            response = await client.post(uri, cookies=token_cookie)
            log.info(f"\nresponse status code: {response.status_code}\n")

            if response.status_code == 200:
                users_access_token = response.cookies.get("users_access_token")
                if users_access_token is None:
                    raise NoTokenException
                log.info(f"\ncookies: {users_access_token}\n")
                bearer_token_dict = {
                    "access_token": users_access_token,
                    "token_type": "bearer",
                }
                return bearer_token_dict
            else:
                auth_response = {
                    "error": "Request failed with status code "
                    + f"{response.status_code}"
                }
                return auth_response

        except Exception as err:
            log.error(f"An error '{type(err)}' "
                      f"occurred while requesting data: {err}")
            message = {
                "message": "Unfortunately, authorization is currently " 
                + "unavailable. In the meantime, you can view the list of "
                + "films with a short description."
                }
            return message
