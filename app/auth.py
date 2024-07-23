# api/auth.py
from pydantic import BaseModel
from fastapi_jwt_auth import AuthJWT
import os

class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv("AUTHJWT_SECRET_KEY", "dj8WxH&rBVo:5yJ")

@AuthJWT.load_config
def get_config():
    return Settings()
