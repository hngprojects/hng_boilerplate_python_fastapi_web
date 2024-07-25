from api.utils.success_response import success_response
from sqlalchemy.orm import Session
from typing import Annotated
from api.db.database import get_db
from api.v1.schemas.user import UserCreate,UserBase
from fastapi import APIRouter,Depends,status,HTTPException
from api.v1.services.user import user_service

'''
The Endpoint created is for the creation of super admins 
'''


superadmin  = APIRouter(
    prefix='/superadmin',
    tags=['Superadmin']
)

db_dependency = Annotated[Session , Depends(get_db)]


@superadmin.post(path='/register', status_code=status.HTTP_201_CREATED)

def register_admin(user : UserCreate , db : db_dependency):
   
    user_created = user_service.create_admin(db=db, schema=user)
    return success_response(
        status_code=201,
        message= 'User Created Successfully',
        data=user_created.to_dict()
    )

    