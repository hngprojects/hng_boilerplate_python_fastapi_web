from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Dict
from api.v1.models.user import WaitlistUser
from api.v1.schemas.waitlist import WaitlistUserCreate
from api.utils.rate_limiter import rate_limit
from api.db.database import get_db

router = APIRouter()


class WaitlistResponse(BaseModel):
    message: str


@router.post("/waitlist", response_model=WaitlistResponse, status_code=201)
@rate_limit(max_calls=5, time_frame=60)
async def signup_waitlist(
    request: Request,
    user: WaitlistUserCreate,
    db: Session = Depends(get_db)
):
    # Check if email already exists
    existing_user = db.query(WaitlistUser).filter(
        WaitlistUser.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    db_user = WaitlistUser(email=user.email, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "You are all signed up!"}
