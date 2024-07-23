from decouple import config
from pydantic import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str = config("DB_HOST")
    DB_PORT: int = config("DB_PORT", default=5432)
    DB_NAME: str = config("DB_NAME")
    DB_USER: str = config("DB_USER")
    DB_PASSWORD: str = config("DB_PASSWORD")
    DB_TYPE: str = config("DB_TYPE", default="postgresql")

    MAIL_USERNAME: str = config("MAIL_USERNAME")
    MAIL_PASSWORD: str = config("MAIL_PASSWORD")
    MAIL_SERVER: str = config("MAIL_SERVER")
    MAIL_PORT: int = config("MAIL_PORT", default=587)
    MAIL_FROM: str = config("MAIL_FROM")
