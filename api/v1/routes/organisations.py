from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.v1.schemas.organisations import OrganizationResponse
from api.v1.services.organisations import get_organization_by_id
from api.v1.services.user import user_service, oauth2_scheme
from api.db.database import get_db

Organisation_id = APIRouter(prefix='/organisation', tags=['Organisation'])


@Organisation_id.get("/{org_id}", response_model=OrganizationResponse)
def read_organization(org_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = user_service.get_current_user(token, db)
    return get_organization_by_id(db, org_id)
