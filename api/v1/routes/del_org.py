from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from api.db.database import get_db
from api.v1.services.organization import delete as delete_organization_service
from api.utils.success_response import success_response
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

superadmin = APIRouter(
    prefix='/superadmin',
    tags=['Superadmin']
)

db_dependency = Annotated[Session, Depends(get_db)]

def get_current_user(token: str = Depends(oauth2_scheme)):
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user

def get_user_from_token(token: str):
    return {"id": 1, "role": "superadmin"}

@superadmin.delete('/organizations/{org_id}', status_code=status.HTTP_200_OK)
def delete_organization(org_id: int, db: db_dependency, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")
    
    result = delete_organization_service(db=db, org_id=org_id)
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    
    return {
        "status": 200,
        "message": "Organization deleted successfully",
        "data": {}
    }
