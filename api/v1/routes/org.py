from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from api.db.database import get_db
from api.v1.models import Organization, User
from api.v1.schemas.org import OrganizationBase
from api.v1.services.user import user_service

org = APIRouter(prefix="/organizations", tags=["Organizations"])

@org.get("/current-user", response_model=List[OrganizationBase], status_code=status.HTTP_200_OK)
def get_user_organizations(current_user: User = Depends(user_service.get_current_user), db: Session = Depends(get_db)):
    '''Endpoint to get all organizations the current user belongs to'''
    user_organizations = current_user.organizations
    return user_organizations
