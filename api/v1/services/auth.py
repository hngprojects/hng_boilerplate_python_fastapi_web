from api.core.base.services import Service
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.schemas.user import TokenData
from api.v1.services.user import user_service
from api.utils.settings import settings
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Tuple
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class AuthService(Service):
    """Auth Service"""

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