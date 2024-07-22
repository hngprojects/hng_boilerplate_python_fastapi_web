from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from api.v1.models.squeeze_model import SqueezeForm, Squeeze
from api.db.database import get_db
from pydantic import BaseModel

class Message(BaseModel):
    message: str

router = APIRouter()

@router.post("/squeeze", response_model=Message)
def create_squeeze(
    *, 
    db: Session = Depends(get_db), 
    squeeze_in: SqueezeForm
):
    squeeze = Squeeze(
        email=squeeze_in.email,
        first_name=squeeze_in.first_name,
        last_name=squeeze_in.last_name,
        phone=squeeze_in.phone,
        location=squeeze_in.location,
        job_title=squeeze_in.job_title,
        company=squeeze_in.company,
        interests=squeeze_in.interests,
        referral_source=squeeze_in.referral_source,
    )
    db.add(squeeze)
    db.commit()
    db.refresh(squeeze)
    return {"message": "Your request has been received. You will get a template shortly."}
