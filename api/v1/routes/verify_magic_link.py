import os
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, constr
from sqlalchemy.orm import Session
from api.v1.services.user import UserService
from database import get_db

router = APIRouter()

# Log setup
log_folder = 'logs'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

log_filename = os.path.join(log_folder, 'verify_magic_link.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Model for magic link verify
class MagicLinkVerify(BaseModel):
    token: constr(strip_whitespace=True, min_length=1)

@router.post("/auth/verify-magic-link")
async def verify_magic_link(
    data: MagicLinkVerify,
    db: Session = Depends(get_db),
    user_service: UserService = Depends(UserService)
):
    token = data.token
    try:
        # Use UserService to verify the token
        user = user_service.verify_access_token(token, HTTPException(
            status_code=400, detail="Invalid or expired token"
        ))
        # Token verified, generate a new authentication token
        auth_token = user_service.create_access_token(user.id)
        return {"auth_token": auth_token, "status": 200}
    except HTTPException as e:
        logger.error(f"Token verification failed: {e.detail}")
        raise e
                  
