# api/utils/settings.py
from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    authjwt_secret_key: str = os.getenv('AUTHJWT_SECRET_KEY','dj8WxH&rBVo:5yJ')

settings = Settings()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))