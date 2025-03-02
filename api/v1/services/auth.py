from api.core.base.services import Service
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.schemas.user import TokenData
from api.v1.services.user import user_service
from api.utils.settings import settings
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from api.core.dependencies.redis_cache import get_redis_client
from sqlalchemy.orm import Session
from typing import Tuple
import jwt
import random
import string

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Initialize Redis client
redis_client = get_redis_client()

class AuthService(Service):
    """Auth Service"""

    @staticmethod
    def cache_unverified_user(email: str, token: str, expiry_minutes: int = 15):
        """Cache unverified user registration details in Redis"""
        key = f"unverified_user:{email}"
        data = json.dumps({"email": email, "token": token})
        redis_client.setex(key, timedelta(minutes=expiry_minutes), data)
        
    @staticmethod
    def generate_verification_token(length: int = 6) -> str:
        """Generate a random alphanumeric token."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def get_unverified_user(email: str):
        """Retrieve unverified user details from Redis"""
        key = f"unverified_user:{email}"
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    

    @staticmethod
    def verify_magic_token(magic_token: str, db: Session) -> Tuple[User, str]:
        """Function to verify magic token"""

        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        token = user_service.verify_access_token(magic_token, credentials_exception)
        user = db.query(User).filter(User.id == token.id).first()
        
        return user, magic_token