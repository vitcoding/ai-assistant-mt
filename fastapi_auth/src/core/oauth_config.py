from httpx_oauth.oauth2 import OAuth2
from pydantic.v1 import BaseSettings, Field


class GoogleOAuth(BaseSettings):
    client_id: str = Field("", env="GOOGLE_CLIENT_ID")
    client_secret: str = Field("", env="GOOGLE_CLIENT_SECRET")
    redirect_uri: str = Field(
        default="http://localhost:8001/api/v1/oauth/google/auth",
        env="GOOGLE_REDIRECT_URI",
    )
    authorize_endpoint: str = Field(
        default="https://accounts.google.com/o/oauth2/auth",
        env="GOOGLE_AUTHORIZE_ENDPOINT",
    )
    access_token_endpoint: str = Field(
        default="https://oauth2.googleapis.com/token",
        env="GOOGLE_ACCESS_TOKEN_ENDPOINT",
    )
    profile_data_endpoint: str = Field(
        default="https://www.googleapis.com/oauth2/v1/userinfo",
        env="GOOGLE_PROFILE_DATA_ENDPOINT",
    )

    class Config:
        env_file = ".oauth.env"
        env_file_encoding = "utf-8"


class YandexOAuth(BaseSettings):
    client_id: str = Field("", env="YANDEX_CLIENT_ID")
    client_secret: str = Field("", env="YANDEX_CLIENT_SECRET")
    redirect_uri: str = Field(
        default="https://oauth.yandex.ru/verification_code",
        env="YANDEX_REDIRECT_URI",
    )
    authorize_endpoint: str = Field(
        default="https://oauth.yandex.ru/authorize",
        env="YANDEX_AUTHORIZE_ENDPOINT",
    )
    access_token_endpoint: str = Field(
        default="https://oauth.yandex.ru/token",
        env="YANDEX_ACCESS_TOKEN_ENDPOINT",
    )
    profile_data_endpoint: str = Field(
        default="https://login.yandex.ru/info",
        env="YANDEX_PROFILE_DATA_ENDPOINT",
    )

    class Config:
        env_file = ".oauth.env"
        env_file_encoding = "utf-8"


class OAuthConfig(BaseSettings):
    yandex: YandexOAuth = YandexOAuth()
    google: GoogleOAuth = GoogleOAuth()

    class Config:
        env_file = ".oauth.env"
        env_file_encoding = "utf-8"


oauth2_settings = OAuthConfig()

oauth = OAuth2(
    oauth2_settings.yandex.client_id,
    oauth2_settings.yandex.client_secret,
    oauth2_settings.yandex.authorize_endpoint,
    oauth2_settings.yandex.access_token_endpoint,
)
