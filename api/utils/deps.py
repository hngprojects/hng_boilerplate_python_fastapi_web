from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from api.db.database import SessionLocal
from api.v1.models.user import User
from uuid import UUID
from passlib.context import CryptContext # for hashing

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db)):
    # Replace with actual user authentication logic
    user = db.query(User).filter(User.id == UUID("user-id")).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")#for choosing password hashing

def hash(password:str):
    return pwd_context.hash(password)

def verify(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)