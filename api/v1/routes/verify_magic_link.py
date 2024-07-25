import logging
import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, constr
from sqlalchemy.orm import Session
from api.v1.services.token_service import TokenService
from api.db.database import get_db

router = APIRouter()


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


class MagicLinkVerify(BaseModel):
    token: constr(strip_whitespace=True, min_length=1)


@router.post("/api/v1/auth/verify-magic-link")
async def verify_magic_link(
        data: MagicLinkVerify,
        db: Session = Depends(get_db),
        token_service: TokenService = Depends(lambda: TokenService())
):
    token = data.token
    if token_service.validate_token(db, token):
        token_service.invalidate_token(db, token)
        auth_token = "authentication-token"
        return {"auth_token": auth_token, "status": 200}
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
