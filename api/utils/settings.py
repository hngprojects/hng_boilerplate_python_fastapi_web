from pydantic_settings import BaseSettings
from decouple import config
from pathlib import Path

# Use this to build paths inside the project
BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    """ Class to hold application's config values."""

    # API_V1_STR: str = "/api/v1"
    # APP_NAME: str = "TicketHub"
    # JWT_SECRET_KEY: str = config("JWT_SECRET_KEY")
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES")

    # Database configurations
    DB_HOST: str = config("DB_HOST", default="localhost")
    DB_PORT: int = config("DB_PORT", default=5432, cast=int)
    DB_USER: str = config("DB_USER", default="postgres")
    DB_PASSWORD: str = config("DB_PASSWORD", default="root")
    DB_NAME: str = config("DB_NAME", default="postgres")
    DB_TYPE: str = config("DB_TYPE", default="postgresql")
    
settings = Settings()
