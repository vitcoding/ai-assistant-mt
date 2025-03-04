from dotenv import load_dotenv
from pydantic.v1 import BaseSettings, Field

load_dotenv()


class TestConfig(BaseSettings):
    service_schema: str = Field(default="http://", env="SERVICE_SСHEMA")
    service_host: str = Field(default="127.0.0.1", env="SERVICE_HOST")
    service_port: int = Field(default=8000, env="SERVICE_PORT")


config = TestConfig()

service_url = (
    f"{config.service_schema}{config.service_host}" f":{config.service_port}"
)
