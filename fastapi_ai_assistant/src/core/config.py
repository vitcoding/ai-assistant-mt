import os
from logging import config as logging_config

from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from pydantic.v1 import BaseSettings, Field

from core.logger import LOGGING

load_dotenv()


class GlobalConfig(BaseSettings):
    project_name: str = Field(
        default="AI Assistant",
    )  # the project name for Swagger docs
    base_dir: str = Field(
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )


# logging settings
logging_config.dictConfig(LOGGING)


class GPTConfig(BaseSettings):
    host: str = Field(default="0.0.0.0:11434")
    model: str = Field(default="llama3.2")

    class Config:
        env_prefix = "GPT_"


class LLMModelConfig(BaseSettings):
    """
    LLM model configuration settings.
    """

    host: str = Field(default="127.0.0.1")
    port: int = Field(default=11434)
    model: str = Field(default="llama3.2:3b")
    provider: str = Field(default="ollama")
    embedding_model: str = Field(default="evilfreelancer/enbeddrus")

    class Config:
        env_prefix = "OLLAMA_"


class VectorDB(BaseSettings):
    """
    Vector db configuration settings.
    """

    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8010)

    class Config:
        env_prefix = "CHROMA_"


class UrlConfig(BaseSettings):
    search: str = Field(default="http://0.0.0.0:8000")

    class Config:
        env_prefix = "URL_SERVICE_"


class AuthConfig(BaseSettings):
    """
    Authentication configuration settings, including secret key, algorithm, and login URL.
    """

    secret_key: str = Field(default="gPaFf9ldf-8lgUFePhe", env="SECRET_KEY")
    algoritm: str = Field(default="HS256", env="ALGORITHM")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "AUTH_"


class Config(BaseSettings):
    """
    Base configuration settings class, combining global, authentication, and MongoDB configurations.
    """

    globals: GlobalConfig = GlobalConfig()
    gpt: GPTConfig = GPTConfig()
    llm: LLMModelConfig = LLMModelConfig()
    vector_db: VectorDB = VectorDB()
    url: UrlConfig = UrlConfig()
    auth: AuthConfig = AuthConfig()


config = Config()

templates = Jinja2Templates(directory="api/v1/templates")
