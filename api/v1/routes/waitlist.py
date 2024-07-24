from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from api.v1.models.waitlist  import Waitlist
from api.v1.schemas.waitlist import WaitlistAddUserSchema
from api.db.database import get_db
from api.v1.services.waitlist_email import send_confirmation_email
from api.utils.logger import logger
from fastapi.responses import JSONResponse

waitlist = APIRouter(prefix="/waitlist", tags=["Waitlist"])


class WaitlistResponse(BaseModel):
    message: str

@waitlist.post("/join", response_model=WaitlistResponse, status_code=201)
async def waitlist_signup(
    request: Request,
    user: WaitlistAddUserSchema,
    db: Session = Depends(get_db)
):
    if not user.full_name:
        logger.error("Full name is required")
        raise HTTPException(status_code=422, detail={"message": "Full name is required", 
                                                       "success": False, "status_code": 422})

    existing_user = db.query(Waitlist).filter(
        Waitlist.email == user.email).first()
    if existing_user:
        logger.error(f"Email already registered: {user.email}")
        raise HTTPException(status_code=400, detail={"message": "Email already registered", 
                                                       "success": False, "status_code": 400})

    db_user = Waitlist(email=user.email, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    try:
        await send_confirmation_email(user.email, user.full_name)
        logger.info(f"Confirmation email sent successfully to {user.email}")
    except HTTPException as e:
        logger.error(f"Failed to send confirmation email: {e.detail}")
        raise HTTPException(
            status_code=500, detail={"message": "Failed to send confirmation email", 
                                     "success": False, "status_code": 500})

    logger.info(f"User signed up successfully: {user.email}")
    return JSONResponse(content={"message": "You are all signed up!"}, status_code=201)
