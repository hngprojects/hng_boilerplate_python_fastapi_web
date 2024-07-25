from pydantic_settings import BaseSettings

class Settings(BaseSettings):
   from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRY: int
    MAIL_PORT: int
    MAIL_SERVER: str
    DB_TYPE: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    PYTHON_ENV: str

    class Config:
        env_file = ".env"
        extra = "forbid"  # Disallow extra fields not defined in the model

settings = Settings()