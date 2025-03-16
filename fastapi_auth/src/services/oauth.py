from abc import ABC
from urllib.parse import urlencode

from httpx import AsyncClient

from core.logger import log
from core.oauth_config import oauth, oauth2_settings
from schemas.user import UserCreate
from services.tools.social_profile import profile_to_user


class OAuthServiceABC(ABC):
    """An abstract OAuth service."""

    async def get_url(self):
        """Returns an url for social oauth."""
        ...

    async def auth(self, code: str):
        """Returns the user's social profile data."""
        ...


class YandexService(OAuthServiceABC):
    """Yandex oauth service."""

    async def get_url(self) -> dict:
        """Returns an url for yandex oauth."""

        url = await oauth.get_authorization_url(
            oauth2_settings.yandex.redirect_uri
        )
        log.info(f"\n{__name__} url: \n{url}\n")
        return {"url": url}

    async def auth(self, code: str) -> UserCreate:
        """Returns the user's social profile data."""

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": oauth2_settings.yandex.client_id,
            "client_secret": oauth2_settings.yandex.client_secret,
        }
        async with AsyncClient() as client:
            response = await client.post(
                oauth2_settings.yandex.access_token_endpoint, data=data
            )
            response_data = response.json()
            access_token = response_data.get("access_token")
            log.info(f"\naccess_token: {access_token}\n")

            response = await client.get(
                oauth2_settings.yandex.profile_data_endpoint,
                headers={
                    "Authorization": f"OAuth {access_token}",
                },
            )

        profile_data = response.json()
        log.info(f"\n{__name__} profile_data: \n{profile_data}\n")

        user_data = profile_to_user(profile_data)
        return user_data


class GoogleService(OAuthServiceABC):
    """Google oauth service."""

    async def get_url(self) -> dict:
        """Returns an url for google oauth."""

        params = {
            "response_type": "code",
            "client_id": oauth2_settings.google.client_id,
            "redirect_uri": oauth2_settings.google.redirect_uri,
            "access_type": "offline",
        }
        url = (
            f"{oauth2_settings.google.authorize_endpoint}?"
            f"{urlencode(params)}&scope=openid%20profile%20email"
        )
        log.info(f"\n{__name__} url: \n{url}\n")
        return {"url": url}

    async def auth(self, code: str) -> UserCreate:
        """Returns the user's social profile data."""

        log.debug(f"\n{__name__} code: \n{code}\n")
        params = {
            "code": code,
            "client_id": oauth2_settings.google.client_id,
            "client_secret": oauth2_settings.google.client_secret,
            "redirect_uri": oauth2_settings.google.redirect_uri,
            "grant_type": "authorization_code",
        }
        headers = {"Accept": "application/json"}
        async with AsyncClient() as client:
            response = await client.post(
                oauth2_settings.google.access_token_endpoint,
                params=params,
                headers=headers,
            )

        log.debug(f"\n{__name__} response: \n{response}\n")
        access_data = response.json()
        log.debug(f"\n{__name__} access_data: \n{access_data}\n")
        access_token = access_data["access_token"]
        log.debug(f"\n{__name__} access_token: \n{access_token}\n")

        async with AsyncClient() as client:
            headers.update({"Authorization": f"Bearer {access_token}"})
            response = await client.get(
                oauth2_settings.google.profile_data_endpoint, headers=headers
            )

        profile_data = response.json()
        log.info(f"\n{__name__} profile_data: \n{profile_data}\n")

        user_data = profile_to_user(profile_data)
        return user_data
