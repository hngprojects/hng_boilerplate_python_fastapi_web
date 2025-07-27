from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta
from api.v1.models.user import User
from api.v1.schemas.token import TokenData
from api.v1.schemas.user import ProfileData
from api.db.database import get_db
from .config import SECRET_KEY, ALGORITHM
from api.v1.services.user import user_service
from api.v1.services.profile import profile_service
from api.v1.services.organisation import organisation_service

import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.debug("Decoding JWT token")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            logger.error("User ID not found in token")
            raise credentials_exception
        logger.debug(f"Token decoded successfully, user ID: {user_id}")
    except PyJWTError as e:
        logger.error(f"JWT error: {e}")
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.error("User not found")
        raise credentials_exception
    logger.debug(f"User found: {user}")
    return user


def get_super_admin(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_current_user(db, token)
    if not user.is_superadmin:
        logger.error("User is not a super admin")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    logger.debug("User is super admin")
    return user


def get_authorized_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
) -> User:
    """
    Dependency to get the current user and check if they are a super admin,
    in the billing department, or an owner.
    """
    if current_user.is_superadmin:
        return current_user
    
    profile = profile_service.fetch_by_user_id(db, current_user.id)
    current_user_profile = ProfileData.model_validate(profile, from_attributes=True)
    if current_user_profile.department == "billing":
        return current_user
    

    organisation = organisation_service.retrieve_user_organizations(current_user, db)
    # Check if the user is an owner
    if "owner" in organisation[0].user_role:
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have the necessary permissions to access this resource."
    )
