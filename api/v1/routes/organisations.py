from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.v1.schemas.organisations import OrganizationResponse
from api.v1.services.organisations import get_organization_by_id
from api.v1.services.user import user_service, UserService
from api.db.database import get_db

Organisation_id = APIRouter(prefix='/organisations', tags=['Organisations'])

# Dependency to get the current user
def get_current_user(token: str = Depends(UserService.oauth2_scheme), db: Session = Depends(get_db)):
    return user_service.get_current_user(token, db)

@Organisation_id.get("/api/v1/organisations/{org_id}", response_model=OrganizationResponse)
def read_organization(org_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Fetch organization by ID.

    - **org_id**: ID of the organization to fetch
    - **current_user**: Automatically injected by FastAPI after verifying JWT token
    """
    return get_organization_by_id(db, org_id)