import os
from logging import config as logging_config

from pydantic.v1 import BaseSettings, Field

from core.logger import LOGGING


class Settings(BaseSettings):
    project_name: str = Field(default="auth", env="PROJECT_NAME")
    redis_host: str = Field(default="127.0.0.1", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="secret", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="auth_db", env="POSTGRES_DB")
    postgres_host: str = Field(default="127.0.0.1", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    secret_key: str = Field(default="gPaFf9ldf-8lgUFePhe", env="SECRET_KEY")
    algoritm: str = Field(default="HS256", env="ALGORITHM")
    jaeger_host: str = Field(default="127.0.0.1", env="JAEGER_AGENT_HOST")
    jaeger_port: int = Field(default=6831, env="JAEGER_AGENT_PORT")
    jaeger_console_messages: bool = Field(
        default=False, env="JAEGER_CONSOLE_MESSAGES"
    )
    base_dir: str = Field(
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        env="BASE_DIR",
    )
    enable_tracer: bool = Field(default=True, env="ENABLE_TRACER")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


logging_config.dictConfig(LOGGING)

settings = Settings()


def get_auth_data():
    return {"secret_key": settings.secret_key, "algorithm": settings.algoritm}
