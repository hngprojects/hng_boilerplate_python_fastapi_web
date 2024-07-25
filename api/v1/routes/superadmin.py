from api.utils.success_response import success_response
from sqlalchemy.orm import Session
from typing import Annotated
from api.db.database import get_db
from api.v1.schemas.user import UserCreate,UserBase
from fastapi import APIRouter,Depends,status,HTTPException
from api.v1.services.user import user_service




superadmin  = APIRouter(
    prefix='/superadmin',
    tags=['Superadmin']
)

db_dependency = Annotated[Session , Depends(get_db)]


@superadmin.post(path='/register', status_code=status.HTTP_201_CREATED, response_model=UserBase)
def register_admin(user : UserCreate , db : db_dependency):

    user_created = user_service.create(db=db, schema=user)
    user_created.is_super_admin = True
    db.commit()

    response_data = {
        'id': str(user_created.id),  # Convert UUID to string
        'first_name': user_created.first_name,
        'last_name': user_created.last_name,
        'username': user_created.username,
        'email': user_created.email,
        'created_at': str(user_created.created_at)  # Ensure created_at is in ISO format
    }

    return success_response(
        status_code=201,
        message= 'User Created Successfully',
        data=response_data
    )
