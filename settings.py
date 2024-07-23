from decouple import config
from pydantic import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str = config("DB_HOST")
    DB_PORT: int = config("DB_PORT", default=5432)
    DB_NAME: str = config("DB_NAME")
    DB_USER: str = config("DB_USER")
    DB_PASSWORD: str = config("DB_PASSWORD")
    DB_TYPE: str = config("DB_TYPE", default="postgresql")
