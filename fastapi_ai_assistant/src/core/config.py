import os
from logging import config as logging_config

from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING

load_dotenv()


class GlobalConfig(BaseSettings):
    project_name: str = Field(
        default="AI Assistant",
    )  # the project name for Swagger docs
    base_dir: str = Field(
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    service_host: str = Field(default="127.0.0.1")
    service_port: int = Field(default=8005)

    @property
    def ai_service_host(self) -> str:
        return f"{self.service_host}:{self.service_port}"


# logging settings
logging_config.dictConfig(LOGGING)


class LLMModelConfig(BaseSettings):
    """
    LLM model configuration settings.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="ollama_",
        extra="ignore",
    )

    host: str = Field(default="127.0.0.1")
    port: int = Field(default=11434)
    model: str = Field(default="llama3.2:3b")
    provider: str = Field(default="ollama")
    embedding_model: str = Field(default="evilfreelancer/enbeddrus")


class VectorDB(BaseSettings):
    """
    Vector db configuration settings.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="chroma_",
        extra="ignore",
    )

    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8010)


class CacheConfig(BaseSettings):
    """Configuration settings for the cache storage."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="redis_",
        extra="ignore",
    )

    host: str = Field(default="127.0.0.1")
    port: int = Field(default=6379)


class UrlConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="url_service_",
        extra="ignore",
    )

    search: str = Field(default="http://0.0.0.0:8000")


class AuthConfig(BaseSettings):
    """
    Authentication configuration settings, including secret key, algorithm,
    and login URL.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="auth_",
        extra="ignore",
    )

    secret_key: str = Field(default="gPaFf9ldf-8lgUFePhe", env="SECRET_KEY")
    algoritm: str = Field(default="HS256", env="ALGORITHM")


class Config(BaseSettings):
    """
    Base configuration settings class, combining global, authentication, and MongoDB configurations.
    """

    globals: GlobalConfig = GlobalConfig()
    llm: LLMModelConfig = LLMModelConfig()
    vector_db: VectorDB = VectorDB()
    cache: CacheConfig = CacheConfig()
    url: UrlConfig = UrlConfig()
    auth: AuthConfig = AuthConfig()


config = Config()

templates = Jinja2Templates(directory="api/v1/templates")
