from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError
from src.utils.logger import logger


class Settings(BaseSettings):
    FRONTEND_URL: str
    BACKEND_URL: str
    MONGODB_URL: str
    DB_NAME: str
    ENVIRONMENT: str
    HF_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


try:
    env = Settings()  # type: ignore
except ValidationError as e:
    missing_fields = [err["loc"][0] for err in e.errors()]
    logger.error(f"Missing environment variables: {missing_fields}")
    exit(1)
