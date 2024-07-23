# generate_token.py
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv("AUTHJWT_SECRET_KEY")

@AuthJWT.load_config
def get_config():
    return Settings()

if __name__ == "__main__":
    auth = AuthJWT()
    token = auth.create_access_token(subject="testuser")
    print(f"Generated JWT Token: {token}")
