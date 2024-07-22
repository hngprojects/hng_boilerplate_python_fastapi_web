from fastapi import FastAPI, Response,status,HTTPException,Depends,APIRouter
from sqlalchemy.orm import Session
from enum import auto
from typing import Optional,List
from api.v1.models.user import User
from api.v1.schemas import schemas
from api.utils import deps
from api.db.database import get_db

router = APIRouter(tags=['users'])

@router.post("/api/v1/users",status_code=status.HTTP_201_CREATED, response_model=schemas.user_output)
def  create_user(user: schemas.createUser,db: Session = Depends(get_db)):

    #hashing the password
    password_hashed = deps.hash(user.password)
    user.password= password_hashed

    #newuser = models.User(**user.dict())
    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get("/api/v1/users/{id}")
def  get_user(id: int,db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user with id:{id} does not exist")
    
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at":user.created_at
    }
    return {"message":"succesfully found","data":user_data}
    

