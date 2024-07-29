from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import (APIRouter, Depends, status, HTTPException)

from api.v1.services.google_oauth import GoogleOauthServices
from api.v1.schemas.google_oauth import IdToken, Tokens
from api.v1.services.google_oauth import GoogleOauthServices
from api.db.database import get_db


google_auth = APIRouter(prefix="/auth", tags=["Authentication"])

@google_auth.post("/google")
async def google_login(id_token: IdToken, db: Annotated[Session, Depends(get_db)],
                       google_service: GoogleOauthServices = Depends()):
    """
    Allows users to login using their google accounts.

    Args:
        id_token: incoming token to verify

    Returns:
        Exception: if error occurs
    """
    access, refresh = google_service.verify_google_token(id_token.id_token, db)
    
    if not access or not refresh:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login failed")
    return Tokens(access_token=access,
                  refresh_token=refresh)