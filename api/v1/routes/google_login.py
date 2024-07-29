
from fastapi import (APIRouter, Depends, status, HTTPException)

from api.v1.services.google_oauth import GoogleOauthServices
from api.v1.schemas.google_oauth import IdToken
from api.v1.services.google_oauth import GoogleOauthServices

google_auth = APIRouter(prefix="/auth", tags=["Authentication"])

@google_auth.post("/google-login")
async def google_login(id_token: IdToken, google_service: GoogleOauthServices = Depends()):
    """
    Allows users to login using their google accounts.

    Args:
        id_token: incoming token to verify

    Returns:
        Exception: if error occurs
    """
    data = await google_service.verify_google_token(id_token.id_token)
    
    if not data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login failed")
    return data
    
