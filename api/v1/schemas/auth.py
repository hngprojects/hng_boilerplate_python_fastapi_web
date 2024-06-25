from uuid import uuid4
from pydantic import BaseModel, model_validator, EmailStr
from typing import Optional
from fastapi import HTTPException, status
from datetime import datetime
from api.db.database import SessionLocal
from api.v1.models.auth import User
from api.core import responses

"""
TODO:   PASSWORD COMPLEXITY VALIDATION ON CREATEUSER SCHEMA
        UNIQUE_ID SHOULD NOT ALREADY EXIST


"""
class Login(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id:int
    email:str

class UserBase(BaseModel):
    first_name: str 
    last_name: str
    email: str
    unique_id: Optional[str] = None
    is_active: bool = True
    date_created: Optional[datetime] = datetime.utcnow()
    last_updated: Optional[datetime] = datetime.utcnow()

    class Config:
        from_attributes = True


class CreateUser(UserBase):
    password: str

    class Config:
        from_attributes = True
       

    #validate email not in use
    @model_validator(mode='before')
    @classmethod
    def validate_email(cls, values):
        email = values.get("email")

        with SessionLocal() as db:
            user_email = db.query(User).filter(User.email == email).first()
            if user_email:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= responses.EMAIL_IN_USE)

        
        return values

class ShowUser(UserBase):
    id: int
    is_deleted: Optional[bool]

    class Config:
        from_attributes=True