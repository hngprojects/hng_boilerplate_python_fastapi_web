from pydantic_settings import BaseSettings
from decouple import config
from pathlib import Path
from pydantic import EmailStr


# Use this to build paths inside the project
BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """ Class to hold application's config values."""

    # API_V1_STR: str = "/api/v1"
    # APP_NAME: str = "TicketHub"
    # JWT_SECRET_KEY: str = config("JWT_SECRET_KEY")
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES")

    # Database configurations
    DB_HOST: str = config("DB_HOST")
    DB_PORT: int = config("DB_PORT", cast=int)
    DB_USER: str = config("DB_USER")
    DB_PASSWORD: str = config("DB_PASSWORD")
    DB_NAME: str = config("DB_NAME")
    DB_TYPE: str = config("DB_TYPE")

    MAIL_USERNAME: str = config("MAIL_USERNAME")
    MAIL_PASSWORD: str = config('MAIL_PASSWORD')
    MAIL_FROM: str = config('MAIL_FROM')
    MAIL_PORT: int = config('MAIL_PORT')
    MAIL_SERVER: str = config('MAIL_SERVER')


settings = Settings()
