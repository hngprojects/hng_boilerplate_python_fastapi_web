from pydantic_settings import BaseSettings
from decouple import config
from pathlib import Path


# Use this to build paths inside the project
BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """ Class to hold application's config values."""

    # API_V1_STR: str = "/api/v1"
    # APP_NAME: str = "TicketHub"
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRY: int = 5
    MAIL_PORT: int = 5432
    MAIL_SERVER: str = "smtp.gmail.com"

    # Database configurations
    DB_HOST: str = config("DB_HOST")
    DB_PORT: int = config("DB_PORT", cast=int)
    DB_USER: str = config("DB_USER")
    DB_PASSWORD: str = config("DB_PASSWORD")
    DB_NAME: str = config("DB_NAME")
    DB_TYPE: str = config("DB_TYPE")
    DB_TYPE: str = "postgresql"
    DB_NAME: str = "dbname"
    DB_USER: str = "username"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    PYTHON_ENV: str = "development"  # Example value

    MAIL_USERNAME: str = config("MAIL_USERNAME")
    MAIL_PASSWORD: str = config('MAIL_PASSWORD')
    MAIL_FROM: str = config('MAIL_FROM')
    MAIL_PORT: int = config('MAIL_PORT')
    MAIL_SERVER: str = config('MAIL_SERVER')
    
    class Config:
        env_file = ".env"
        extra = "forbid"  # Prevent extra fields not defined in the model


settings = Settings()