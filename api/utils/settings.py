from pydantic_settings import BaseSettings
from decouple import config
from pathlib import Path


# Use this to build paths inside the project
BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """ Class to hold application's config values."""
    
    SECRET_KEY: str = config("SECRET_KEY")
    ALGORITHM: str = config("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_EXPIRY: int = config("JWT_REFRESH_EXPIRY")

    # Database configurations
    DB_HOST: str = config("DB_HOST")
    DB_PORT: int = config("DB_PORT", cast=int)
    DB_USER: str = config("DB_USER")
    DB_PASSWORD: str = config("DB_PASSWORD")
    DB_NAME: str = config("DB_NAME")
    DB_TYPE: str = config("DB_TYPE")

    MAIL_USERNAME: str = config("MAIL_USERNAME")
    MAIL_PASSWORD: str = config("MAIL_PASSWORD")
    MAIL_FROM: str = config("MAIL_FROM")
    MAIL_PORT: int = config("MAIL_PORT")
    MAIL_SERVER: str = config("MAIL_SERVER")

    FLUTTERWAVE_SECRET: str = config("FLUTTERWAVE_SECRET")

    TWILIO_ACCOUNT_SID: str = config("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: str = config("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: str = config("TWILIO_PHONE_NUMBER")


settings = Settings()
