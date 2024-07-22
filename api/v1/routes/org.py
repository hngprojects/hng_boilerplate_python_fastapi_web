from fastapi import FastAPI, Response,status,HTTPException,Depends,APIRouter
from sqlalchemy.orm import Session
from enum import auto
from typing import Optional,List

from api.utils import oauth2
from api.v1 import models,schemas
from api.v1.schemas import schemas
from api import utils
from api.v1.models.user import User
from api.v1.models.org import Organization
from api.v1.schemas import schemas
from api.db.database import get_db

router = APIRouter(tags=['org'])

#here we protect org using       get_current_user:int = Depends(oauth2.get_current_user)
@router.post("/api/v1/org",status_code=status.HTTP_201_CREATED, response_model=schemas.org_output)
def create_org(org: schemas.createOrg, db: Session = Depends(get_db)):
    current_user_id = "0669d4f6-c70c-7530-8000-59806c951d00"  # Replace with actual current user ID
    #check if he is admin
    is_admin = db.query(User).filter(User.id == current_user_id).first()
    if not (is_admin.is_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"you cant create new organisation")
        
    #org_dict = org.dict()  # Convert Pydantic model to dictionary
    #org_dict['user_id'] = current_user_id  # Update the user_id
    new_org = Organization(**org.model_dump())  # Create new organization instance
    db.add(new_org)  # Add to session
    db.commit()  # Commit transaction
    db.refresh(new_org)  # Refresh instance with new data
    return new_org  # Return the newly created organization


@router.get("/api/v1/org",response_model=List[schemas.org_output])
def  get_org(db: Session = Depends(get_db)):
    org = db.query(models.org).all()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"org does not exist")
    
    return org
    


@router.get("/api/v1/org/{id}")
def  get_specific_org(id: int,db: Session = Depends(get_db)):
    org = db.query(models.org).filter(models.org.id == id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user with id:{id} does not exist")
    
    user_data = {
        "id": org.id,
        "title": org.title,
        "content": org.content,
    }
    return {"message":"succesfully found","data":user_data}
    

